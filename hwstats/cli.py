import logging
from multiprocessing import Process

from hwstats import DB_PATH
from hwstats.frontend import start_app
from hwstats.log_config import configure_logging
from hwstats.monitor import start_metrics_collection

COLLECTION_INTERVAL_SECONDS = 0.1
TIMEOUT_SECONDS = 0


if __name__ == "__main__":
    configure_logging()
    logger = logging.getLogger("hwstats")
    logger.info("Starting the Hardware Stats monitoring application")

    metrics_process = Process(
        target=start_metrics_collection,
        args=[COLLECTION_INTERVAL_SECONDS],
        kwargs={"timeout": TIMEOUT_SECONDS, "db_path": DB_PATH},
    )
    app_process = Process(target=start_app)

    metrics_process.start()
    app_process.start()

    metrics_process.join()
    app_process.join()
