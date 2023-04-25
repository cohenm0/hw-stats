import os
from pathlib import Path

DB_NAME = "tmp_metrics.db"

"""
How often to collect metrics and attempt to write them to the database. This value is
very impactful on application perforance and also impacts the risk of concurrency errors.
If the value is too large then metric data loses resoltion, if the value is too small then
the DB write queue fills up which slows queries and increases the chance of concurrency errors.
We've found that a value of 0.5 seconds generally works well.
"""
COLLECTION_INTERVAL_SECONDS = 0.05

# A timeout of 0 means that the application will run until the user kills it
TIMEOUT_SECONDS = 0

HWSATS_PROJECT_DIR = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))
OUT_DIR = Path(os.path.join(HWSATS_PROJECT_DIR, "out"))
os.makedirs(OUT_DIR, exist_ok=True)

DB_PATH = os.path.join(OUT_DIR, DB_NAME)
