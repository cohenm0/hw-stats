import os
from pathlib import Path

DB_NAME = "tmp_metrics.db"

HWSATS_PROJECT_DIR = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))
OUT_DIR = Path(os.path.join(HWSATS_PROJECT_DIR, "out"))
os.makedirs(OUT_DIR, exist_ok=True)

DB_PATH = Path(os.path.join(OUT_DIR, DB_NAME))
