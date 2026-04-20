from flask import Flask, request

from .auth import auth
from .profile import profile

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config.from_pyfile("../config.py")

from . import views


@app.context_processor
def inject_theme() -> dict[str, str]:
    return {"active_theme": request.cookies.get("color_scheme", "light")}


app.register_blueprint(auth)
app.register_blueprint(profile)
