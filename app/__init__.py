import logging
from pathlib import Path

from flask import Flask


def configure_contact_logger(app: Flask) -> None:
    logger = logging.getLogger(f"lab5.contact.{id(app)}")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    log_path = Path(app.config["CONTACT_LOG_PATH"])
    log_path.parent.mkdir(parents=True, exist_ok=True)

    handler = logging.FileHandler(log_path, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s | %(message)s"))
    logger.handlers.clear()
    logger.addHandler(handler)

    app.extensions["contact_logger"] = logger


app = Flask(__name__, template_folder="templates", static_folder="static")
app.config.from_pyfile("../config.py")

configure_contact_logger(app)

from . import views
