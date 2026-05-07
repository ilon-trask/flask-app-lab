from __future__ import annotations

import os

import pytest

os.environ["FLASK_CONFIG"] = "testing"

from app import app as flask_app
from app import db


@pytest.fixture
def app(tmp_path):
    flask_app.config.update(
        TESTING=True,
        WTF_CSRF_ENABLED=False,
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{tmp_path / 'test.sqlite'}",
    )

    with flask_app.app_context():
        db.drop_all()
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()

