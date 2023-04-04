import os
from pathlib import Path

from sqlalchemy.engine.base import Engine

from hwstats.backend import get_db_connection


def test_get_db_connection(tmp_path: Path) -> None:
    """Test the get_db_connection function"""
    database_path = tmp_path / "test.db"
    engine = get_db_connection(database_path)
    assert isinstance(engine, Engine)
    assert os.path.exists(database_path)
