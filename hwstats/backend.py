import logging
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine

logger = logging.getLogger(__name__)


def get_db_connection(database_path: Path) -> Engine:
    """
    Get a connection to the database and if the database does not exist, create it.
    Note that if you've changed the models, you'll need to delete the database file.
    :return: SQLAlchemy engine
    """
    logger.info(f"Connecting to database at {database_path}")
    return create_engine(f"sqlite:///{database_path}")
