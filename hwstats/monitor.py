import logging
from multiprocessing import Queue as mpQueue
from queue import Empty, Queue
from sqlite3 import OperationalError
from threading import Event, Thread
from time import sleep, time

import psutil
import xxhash
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import Session

from hwstats import DB_PATH, models
from hwstats.backend import get_db_connection

logger = logging.getLogger(__name__)


def start_metrics_collection(
    collection_interval: float,
    timeout: float = 0,
    db_path: str = DB_PATH,
    msg_queue: mpQueue = None,
) -> None:
    """
    Start collecting metrics
    :param collection_interval: How often to collect metrics
    :param timeout: How long to collect metrics for. If 0, collect forever
    :param db_path: Path to the database file
    :param msg_queue: Multiprocessing queue for receiving messages to stop the metric collection
    """
    engine = get_db_connection(db_path)
    models.Base.metadata.create_all(engine)

    # We use a queue so that DB writes can be asynchronus to metric collection
    data_queue = Queue()
    shut_down = Event()
    db_writer_thread = Thread(
        target=write_to_db,
        args=(engine, data_queue, shut_down),
        kwargs={"interval": collection_interval},
        name="db_writer_thread",
    )
    db_writer_thread.start()

    start_time = time()
    logger.info("Starting collection")
    while True:
        for _process in psutil.process_iter():
            try:
                data = get_process_data(_process)
                data_queue.put(data)

            # If the process dies before the iterator gets to it then skip it
            except (psutil.NoSuchProcess, FileNotFoundError):
                logger.debug(f"Skipping dead process {_process}")

        sleep(collection_interval)
        try:
            kill = msg_queue.get_nowait()
        except Empty:
            kill = False
        if time() - start_time > timeout and timeout != 0 or kill:
            logger.warning("Stopping collection")
            shut_down.set()
            db_writer_thread.join(timeout=collection_interval)
            return


def get_process_data(process: psutil.Process) -> tuple:
    """Get data for a process"""
    # Getting process info as a dict uses the oneshot method under the covers. This might be less
    # efficient than using the oneshot method directly, but for some reason calling the model build
    # methods seemed to exit the oneshot context manager and lead to bad data.
    process_dict = process.as_dict()
    process_dict["pidHash"] = hash_process(process_dict)

    _sysprocess = models.build_sysprocess_from_process(process_dict)
    _cpu = models.build_cpu_from_process(process_dict)
    _memory = models.build_memory_from_process(process_dict)
    _disk = models.build_disk_from_process(process_dict)

    return (_sysprocess, _cpu, _memory, _disk)


def write_to_db(engine: Engine, data_queue: Queue, shutdown: Event, interval: float = 0.1) -> None:
    """Write data from the queue to the database"""
    with Session(engine) as session:
        while not shutdown.is_set():
            _sysprocess, _cpu, _memory, _disk = data_queue.get()
            try:
                session.merge(_sysprocess)
                session.add_all([_cpu, _memory, _disk])
                session.commit()
            except OperationalError:
                session.rollback()
                logger.error(f"The database is locked. Retrying in {interval} seconds")

            # Without a sleep here the chance of DB lock is much higher and
            # query performance is noticably slower
            sleep(interval)

        session.commit()
        logger.debug("DB writer thread shutting down")
        return


def hash_process(process_dict: dict) -> None:
    """Hash the process id, name, and create time to get a unique id for the process"""
    id_str = f"{process_dict['pid']}, {process_dict['name']}, {process_dict['create_time']}"
    return xxhash.xxh64(id_str).hexdigest()
