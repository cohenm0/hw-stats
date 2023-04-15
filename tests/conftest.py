import os

import pytest

from hwstats import OUT_DIR


@pytest.fixture
def db_path() -> str:
    """
    Create a test database path, and then delete the database after all tests are done
    :return: Path to the test database
    """
    os.makedirs(OUT_DIR, exist_ok=True)
    file_path = os.path.join(OUT_DIR, "test.db")
    yield file_path
    os.remove(file_path)
