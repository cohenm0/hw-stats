import os
from time import sleep

import psutil
from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import Session

from hwstats import models

COLLECTION_INTERVAL = 0.1


def main():
    """Main function"""
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
    os.makedirs(out_dir, exist_ok=True)
    db_path = os.path.join(out_dir, "tmp_metrics.db")
    engine = create_engine(f"sqlite:///{db_path}", echo=True)

    models.Base.metadata.create_all(engine)

    while True:
        collect_metrics(engine)
        sleep(COLLECTION_INTERVAL)


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
