import logging
import os
import sys

from flask import Flask, render_template
from jinja2 import Environment, PackageLoader
from plotly import graph_objects as go
from sqlalchemy.orm import Session

from hwstats import DB_PATH
from hwstats.backend import (
    get_db_connection,
    index_table_query,
    query_cpu_percent_with_time,
)
from hwstats.models import Base

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

    process_list = index_table_query(session)

    return render_template("index.html", process_list=process_list)


@app.route("/process/<int:pid_hash>/plot")
def process_plot(pid_hash: int) -> str:
    """Retrieve the process plot page"""
    engine = get_db_connection(DB_PATH)
    session = Session(engine)
    cpu_data = query_cpu_percent_with_time(pid_hash, session)

    # Create a list of timestamps and CPU percentages
    timestamps = [row[0] for row in cpu_data]
    cpu_percentages = [row[1] for row in cpu_data]

    # Create a plot using plotly
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=timestamps, y=cpu_percentages, mode="lines"))

    # Render the template with the plot
    return render_template("plot.html", plot=fig.to_html(full_html=False))
    # return render_template("process_plot.html", pid_hash=pid_hash)
