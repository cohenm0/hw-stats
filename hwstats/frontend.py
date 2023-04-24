import logging
import os
import sys

from flask import Flask, render_template
from jinja2 import Environment, PackageLoader
from plotly import graph_objects as go
from plotly.graph_objects import Figure
from sqlalchemy.orm import Session

from hwstats import DB_PATH
from hwstats.backend import (
    get_db_connection,
    index_table_query,
    query_cpu_percent_with_time,
    query_memory_percent_with_time,
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


@app.route("/process/<string:pid_hash>/plot")
def process_plot(pid_hash: str) -> str:
    """Retrieve the process plot page"""
    engine = get_db_connection(DB_PATH)
    session = Session(engine)

    cpu_fig = get_time_plot_fig(pid_hash, session, query_cpu_percent_with_time)
    mem_fig = get_time_plot_fig(pid_hash, session, query_memory_percent_with_time)
    return render_template(
        "plot.html",
        cpu_plot=cpu_fig.to_html(full_html=False),
        mem_plot=mem_fig.to_html(full_html=False),
    )


def get_time_plot_fig(pid_hash: str, session: Session, query: callable) -> Figure:
    """
    Return the CPU plot as a plotly figure
    :param pid_hash: pidHash of the process
    :param session: SQLAlchemy session
    :param query: function to query a list of tuples containing the timestamp and data
    """
    query_result = query(pid_hash, session)

    # Create a list of timestamps and data
    timestamps = [row.timestamp for row in query_result]
    data = [row.data for row in query_result]

    # Create a plot using plotly
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=timestamps, y=data, mode="lines"))

    return fig


@app.route("/shutdown", methods=["POST"])
def shutdown():
    os.system("sudo shutdown -h now")
    return "Shutting down..."


if __name__ == "__main__":
    app.run(debug=True)
