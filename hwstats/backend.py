import logging

from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from hwstats.models import CPU, Memory, SysProcess

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


def index_table_query(session: Session) -> list[tuple]:
    """
    Query the DB session to get a list of tuples containing the process information
    :param session: SQLAlchemy session
    :return: list of tuples containing process information
    """
    statement = (
        session.query(
            SysProcess.name,
            SysProcess.pid,
            SysProcess.createTime,
            SysProcess.pidHash,
            func.avg(CPU.cpuPercent).label("avg_cpu_percent"),
            func.avg(Memory.memoryPercent).label("avg_memory_percent"),
        )
        .outerjoin(CPU, SysProcess.pidHash == CPU.pidHash)
        .outerjoin(Memory, SysProcess.pidHash == Memory.pidHash)
        .group_by(SysProcess.name, SysProcess.pid, SysProcess.createTime, SysProcess.pidHash)
    )
    return statement.all()


def query_cpu_percent_with_time(pid_hash: int, session: Session) -> list[tuple]:
    """
    Query the DB session to get a list of tuples containing the CPU percent and measurement time
    :param pid_hash: pidHash of the process
    :param session: SQLAlchemy session
    :return: list of tuples containing CPU percent and measurement time
    """
    result = (
        session.query(CPU.measurementTime, CPU.cpuPercent).filter(CPU.pidHash == pid_hash).all()
    )
    return result
