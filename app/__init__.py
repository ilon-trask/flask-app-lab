from flask import Flask

from .users import users
from .products import products

app = Flask(__name__)
from . import views

app.config.from_pyfile("../config.py")

app.register_blueprint(users)
app.register_blueprint(products)
