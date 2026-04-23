from . import app
from flask import redirect, url_for, render_template


@app.route("/")
def index():
    return redirect(url_for("posts.list_posts"))


@app.errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404
