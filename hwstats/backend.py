import logging
import os

from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(filename)s:%(lineno)d:%(levelname)s:%(message)s")

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
logger.addHandler(ch)


def get_db_connection() -> Engine:
    """
    Get a connection to the database and if the database does not exist, create it.
    Note that if you've changed the models, you'll need to delete the database file.
    :return: SQLAlchemy engine
    """
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    out_dir = os.path.join(base_dir, "out")
    os.makedirs(out_dir, exist_ok=True)
    db_path = os.path.join(out_dir, "tmp_metrics.db")
    # pylint: disable=logging-fstring-interpolation
    logger.info(f"Connecting to database at {db_path}")
    return create_engine(f"sqlite:///{db_path}")
