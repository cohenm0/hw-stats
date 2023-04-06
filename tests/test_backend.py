import os

from sqlalchemy.engine.base import Engine

from hwstats.backend import get_db_connection
from hwstats.models import Base


def test_get_db_connection(db_path: str) -> None:
    """Test the get_db_connection function"""
    engine = get_db_connection(db_path)
    # The db is not created until we call create_all
    Base.metadata.create_all(engine)
    assert isinstance(engine, Engine)
    assert os.path.exists(db_path)

    # Cleanup
    os.remove(db_path)
