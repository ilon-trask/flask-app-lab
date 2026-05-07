from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

load_dotenv()

from app.config import config_by_name

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()


app = Flask(__name__, instance_relative_config=True)
config_name = os.getenv("FLASK_CONFIG") or (
    "testing" if "unittest" in sys.modules else "development"
)
app.config.from_object(config_by_name[config_name])

Path(app.instance_path).mkdir(parents=True, exist_ok=True)
db.init_app(app)
migrate.init_app(app, db)
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message_category = "warning"

from . import views
from .models import User
from .books import books_bp

app.register_blueprint(books_bp, url_prefix="/books")


@login_manager.user_loader
def load_user(user_id: str) -> User | None:
    return db.session.get(User, int(user_id))


@app.shell_context_processor
def make_shell_context() -> dict[str, object]:
    from app.books.models import Book, Genre

    return {
        "db": db,
        "User": User,
        "Genre": Genre,
        "Book": Book,
    }
