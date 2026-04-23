from __future__ import annotations

import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_DATABASE_URL = "sqlite:///instance/data.sqlite"


def _normalize_sqlite_url(url: str) -> str:
    if url.startswith("sqlite:///") and not url.startswith("sqlite:////"):
        relative_path = url.removeprefix("sqlite:///")
        if relative_path != ":memory:":
            return f"sqlite:///{(BASE_DIR / relative_path).resolve()}"
    return url


def _database_uri() -> str:
    url = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)

    if url.startswith("sqlite"):
        return _normalize_sqlite_url(url)

    return _normalize_sqlite_url(DEFAULT_DATABASE_URL)


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    SQLALCHEMY_DATABASE_URI = _database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TESTING = False


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = _normalize_sqlite_url(
        os.getenv("TEST_DATABASE_URL", "sqlite:///:memory:")
    )


class ProductionConfig(Config):
    DEBUG = False


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}
