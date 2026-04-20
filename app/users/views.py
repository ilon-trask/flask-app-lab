from flask import render_template, request, url_for, redirect
from . import users


@users.route("/hi/<string:name>")
def greetings(name):
    name = name.upper()
    age = request.args.get("age", None, int)

    return render_template("hi.html", name=name, age=age)


@users.route("/admin")
def admin():
    to_url = url_for("users.greetings", name="administrator", age=45, _external=True)
    print("to_url", to_url)
    return redirect(to_url)
