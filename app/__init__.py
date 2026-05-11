from flask import Flask
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from .config import Config
from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        }
    )


db = SQLAlchemy()
migrate = Migrate()


bcrypt = Bcrypt()

from . import models


def create_app():
    app = Flask(__name__, template_folder="./templates/", static_folder="./static")
    app.config.from_object(Config)

    from .views import main

    app.register_blueprint(main)

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)

    return app
