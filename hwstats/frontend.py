import logging
import os
import sys

from flask import Flask, render_template
from jinja2 import Environment, PackageLoader
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from hwstats import DB_PATH
from hwstats.backend import get_db_connection
from hwstats.models import CPU, Base, Memory, SysProcess

logger = logging.getLogger(__name__)

# When running from a pyinstaller executable, the templates and static folders are not found
# Use sys._MEIPASS, to find the  PyInstaller temporary budle folder and pass it to Flask
# Reference: https://github.com/ciscomonkey/flask-pyinstaller
if getattr(sys, "frozen", False):
    template_folder = os.path.join(sys._MEIPASS, "templates")
    static_folder = os.path.join(sys._MEIPASS, "static")
    logger.debug(f"Using template folder: {template_folder}")
    app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
else:
    app = Flask(__name__)


def start_app():
    """Start the Flask app"""
    app.run()


def round_filter(value, precision=2):
    return round(value, precision)


# Add the round function to the template environment's globals
env = Environment(loader=PackageLoader(app.name, "templates"))
env.filters["round"] = round_filter


@app.route("/")
def index() -> str:
    """Retrieve the index page"""
    engine = get_db_connection(DB_PATH)
    Base.metadata.create_all(engine)
    session = Session(engine)
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
    process_list = statement.all()

    return render_template("index.html", process_list=process_list)
