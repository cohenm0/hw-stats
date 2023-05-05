import logging
import os
import sys

from flask import Flask, render_template

# from jinja2 import Environment, PackageLoader
from plotly import graph_objects as go
from plotly.graph_objects import Figure
from plotly.subplots import make_subplots
from sqlalchemy.orm import Session

from hwstats import DB_PATH
from hwstats.backend import (
    get_db_connection,
    index_table_query,
    query_cpu_percent_with_time,
    query_Disk_read_write_with_time,
    query_memory_percent_with_time,
)
from hwstats.models import Base

logger = logging.getLogger(__name__)

# Build the engine, create the tables if they don't exist, and create a session
# We do this once, when the app starts, so that we don't have to do it for every request
ENGINE = get_db_connection(DB_PATH)
Base.metadata.create_all(ENGINE)

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
# env = Environment(loader=PackageLoader(app.name, "templates"))
# env.filters["round"] = round_filter


@app.route("/")
def index() -> str:
    """Retrieve the index page"""
    with Session(ENGINE) as session:
        process_list = index_table_query(session)

    return render_template("index.html", process_list=process_list)


@app.route("/process/<string:pid_hash>/plot")
def process_plot(pid_hash: str) -> str:
    """Retrieve the process plot page"""
    with Session(ENGINE) as session:
        cpu_fig = get_time_plot_fig(pid_hash, session, query_cpu_percent_with_time, "Cpu")
        mem_fig = get_time_plot_fig(pid_hash, session, query_memory_percent_with_time, "Memory")
        disk_fig = get_read_write_plot_fig(pid_hash, session, query_Disk_read_write_with_time)

    return render_template(
        "plot.html",
        cpu_plot=cpu_fig.to_html(full_html=False),
        mem_plot=mem_fig.to_html(full_html=False),
        disk_plot=disk_fig.to_html(full_html=False),
    )


def get_time_plot_fig(pid_hash: str, session: Session, query: callable, name: str) -> Figure:
    """
    Return the CPU plot as a plotly figure
    :param pid_hash: pidHash of the process
    :param session: SQLAlchemy session
    :param query: function to query a list of tuples containing the timestamp and data
    :param name: Adding the name of the plot to the plot
    """
    query_result = query(pid_hash, session)

    # Create a list of timestamps and data
    timestamps = [row.timestamp for row in query_result]
    data = [row.data for row in query_result]

    # Create a plot using plotly
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=timestamps, y=data, mode="lines"))
    fig.update_layout(title_text=f"{name} usage over time")

    fig.update_xaxes(title_text="<b>Time</b>")

    fig.update_yaxes(title_text="<b>Usage</b>")

    return fig


def get_read_write_plot_fig(pid_hash: str, session: Session, query: callable) -> Figure:
    query_result = query(pid_hash, session)

    timestamp = [row.timestamp for row in query_result]
    readData = [row.readData for row in query_result]
    writeData = [row.writeData for row in query_result]

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Scatter(x=timestamp, y=readData, mode="lines", name="readData"),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(x=timestamp, y=writeData, mode="lines", name="writedData"),
        secondary_y=True,
    )
    fig.update_layout(title_text="Read and Write on disk over time")

    fig.update_xaxes(title_text="<b>Time</b>")

    fig.update_yaxes(title_text="<b>primary</b> yaxis read Data", secondary_y=False)
    fig.update_yaxes(title_text="<b>secondary</b> yaxis write Data", secondary_y=True)

    return fig
