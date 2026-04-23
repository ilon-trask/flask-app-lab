from __future__ import annotations

from flask import Blueprint

posts_bp = Blueprint(
    "posts",
    __name__,
    template_folder="templates",
    static_folder="static",
)

from . import views
