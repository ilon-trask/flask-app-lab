from flask import flash, redirect, render_template, request, session, url_for
from dataclasses import dataclass

from . import auth


@dataclass(frozen=True)
class DemoUser:
    username: str
    password: str


DEMO_USER = DemoUser(username="username", password="password")


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if username == DEMO_USER.username and password == DEMO_USER.password:
            session["username"] = username
            flash("You have logged in successfully.", "success")
            return redirect(url_for("profile.profile_func"))

        flash("Invalid username or password.", "danger")
        return redirect(url_for("auth.login"))

    return render_template(
        "auth/login.html",
        title="Login",
        demo_username=DEMO_USER.username,
        demo_password=DEMO_USER.password,
    )


@auth.post("/logout")
def logout():
    session.pop("username", None)
    flash("You have logged out.", "info")
    return redirect(url_for("auth.login"))
