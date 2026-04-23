from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

load_dotenv()

from app.config import config_by_name

db = SQLAlchemy()
migrate = Migrate()


app = Flask(__name__, instance_relative_config=True)
config_name = os.getenv("FLASK_CONFIG") or (
    "testing" if "unittest" in sys.modules else "development"
)
app.config.from_object(config_by_name[config_name])

Path(app.instance_path).mkdir(parents=True, exist_ok=True)
db.init_app(app)
migrate.init_app(app, db)

from . import views
from .posts import posts_bp

app.register_blueprint(posts_bp, url_prefix="/post")
