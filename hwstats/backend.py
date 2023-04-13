import logging

from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import Session

from hwstats.models import CPU, SysProcess

logger = logging.getLogger(__name__)


def get_db_connection(database_path: str) -> Engine:
    """
    Get a connection to the database. If the database does not exist, it will be created
    once we try to write to it.
    Note that if you've changed the models, you'll need to delete the database file.
    :param database_path: Absolute path to the database file
    :return: SQLAlchemy engine
    """
    logger.info(f"Connecting to database at {database_path}")
    return create_engine(f"sqlite:///{database_path}")


def get_cpu_percents_for_pidHash(pid_hash: int, session: Session) -> list[float]:
    """
    Query the DB session to get a list of CPU percents for a given pidHash
    :param pid_hash: pidHash of the process
    :param session: SQLAlchemy session
    :return: list of records containing CPU percent
    """
    result = (
        session.query(CPU.cpuPercent)
        .filter(CPU.pidHash == SysProcess.pidHash)
        .filter(SysProcess.pidHash == pid_hash)
        .all()
    )
    cpu_percents = [row[0] for row in result]
    return cpu_percents
