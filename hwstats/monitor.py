import logging
from time import sleep, time

import psutil
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import Session

from hwstats import models
from hwstats.backend import get_db_connection

logger = logging.getLogger(__name__)

COLLECTION_INTERVAL = 0.1
TIMEOUT = 10


async def start_metrics_collection():
    """Start collecting metrics"""
    # SQLAlchemy logging: https://docs.sqlalchemy.org/en/20/core/engines.html#configuring-logging
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)

    engine = get_db_connection()
    models.Base.metadata.create_all(engine)

    start_time = time()
    logger.info("Starting collection")
    while True:
        collect_metrics(engine)
        sleep(COLLECTION_INTERVAL)
        if time() - start_time > TIMEOUT:
            break


def collect_metrics(engine: Engine) -> None:
    """Collect metrics from the system and store them in the database"""
    with Session(engine) as session:
        for _process in psutil.process_iter():
            with _process.oneshot():
                _sysprocess = models.build_sysprocess_from_process(_process)

                _cpu = models.build_cpu_from_process(_process)

                session.merge(_sysprocess)
                session.add_all([_cpu])
                session.commit()
