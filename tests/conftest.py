import os

import pytest

from hwstats import OUT_DIR


@pytest.fixture
def db_path() -> str:
    """Create a test database path"""
    os.makedirs(OUT_DIR, exist_ok=True)
    return os.path.join(OUT_DIR, "test.db")
