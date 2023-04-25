import logging
from queue import Queue
from sqlite3 import OperationalError
from threading import Thread
from time import sleep, time

import psutil
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import Session

from hwstats import DB_PATH, models
from hwstats.backend import get_db_connection

logger = logging.getLogger(__name__)


def start_metrics_collection(
    collection_interval: float, timeout: float = 0, db_path: str = DB_PATH
) -> None:
    """
    Start collecting metrics
    :param collection_interval: How often to collect metrics
    :param timeout: How long to collect metrics for. If 0, collect forever
    :param db_path: Path to the database file
    """
    engine = get_db_connection(db_path)
    models.Base.metadata.create_all(engine)

    data_queue = Queue()
    db_writer_thread = Thread(
        target=write_to_db, args=(engine, data_queue), kwargs={"interval": collection_interval}
    )
    db_writer_thread.start()

    start_time = time()
    logger.info("Starting collection")
    while True:
        for _process in psutil.process_iter():
            try:
                with _process.oneshot():
                    _sysprocess = models.build_sysprocess_from_process(_process)
                    _cpu = models.build_cpu_from_process(_process)
                    _memory = models.build_memory_from_process(_process)
                    _disk = models.build_disk_from_process(_process)

                    data_queue.put((_sysprocess, _cpu, _memory, _disk))

            # If the process dies before the iterator gets to it then skip it
            except (psutil.NoSuchProcess, FileNotFoundError):
                pass

        sleep(collection_interval)
        if time() - start_time > timeout and timeout != 0:
            logger.warning("Stopping collection")
            data_queue.put(None)
            db_writer_thread.join()
            return


def write_to_db(engine: Engine, data_queue: Queue, interval: float = 0.1) -> None:
    """Write data from the queue to the database"""
    with Session(engine) as session:
        while True:
            data = data_queue.get()
            if data is None:
                session.commit()
                return

            _sysprocess, _cpu, _memory, _disk = data
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
