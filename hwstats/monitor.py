import os
from time import sleep, time

import psutil
from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import Session

from hwstats import models

COLLECTION_INTERVAL = 0.1
TIMEOUT = 30


def main():
    """Main function"""

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    out_dir = os.path.join(base_dir, "out")
    os.makedirs(out_dir, exist_ok=True)
    db_path = os.path.join(out_dir, "tmp_metrics.db")
    engine = create_engine(f"sqlite:///{db_path}", echo=True)

    models.Base.metadata.create_all(engine)

    start_time = time()
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


if __name__ == "__main__":
    main()
