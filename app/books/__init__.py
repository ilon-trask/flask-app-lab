from __future__ import annotations

from flask import Blueprint

books_bp = Blueprint(
    "books",
    __name__,
    template_folder="templates",
    static_folder="static",
)

from . import views
