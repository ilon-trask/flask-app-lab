from flask import Blueprint


products = Blueprint(
    "products", __name__, template_folder="templates/products", static_folder="static"
)

from . import views
