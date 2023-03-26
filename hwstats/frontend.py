import os
import sys

from flask import Flask, render_template
from sqlalchemy import select
from sqlalchemy.orm import Session

from hwstats.backend import get_db_connection
from hwstats.models import Base, SysProcess

# When running from a pyinstaller executable, the templates and static folders are not found
# Use sys._MEIPASS, to find the  PyInstaller temporary budle folder and pass it to Flask
# Reference: https://github.com/ciscomonkey/flask-pyinstaller
if getattr(sys, "frozen", False):
    template_folder = os.path.join(sys._MEIPASS, "templates")
    static_folder = os.path.join(sys._MEIPASS, "static")
    app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
else:
    app = Flask(__name__)


async def start_app():
    """Start the Flask app"""
    app.run()


@app.route("/")
def index():
    """Retrieve the index page"""
    engine = get_db_connection()
    Base.metadata.create_all(engine)
    session = Session(engine)
    statement = select(SysProcess)
    process_list = session.execute(statement).scalars().all()
    # TODO: we can't close the session here because the template needs it still.
    # Another option would be to try eagerly loading the relationships
    # https://docs.sqlalchemy.org/en/20/errors.html#error-bhk3
    # session.close()

    return render_template("index.html", process_list=process_list)
