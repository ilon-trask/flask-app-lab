from flask import (
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
    session,
)

from .form_state import restore_form_state, stash_form_state
from .forms import ContactForm, LoginForm
from . import app

from dataclasses import dataclass


@app.route("/")
def index():
    return render_template("index.html", title="Home")


@app.route("/contact", methods=["GET", "POST"])
def contact():
    form = ContactForm()

    if request.method == "GET":
        restore_form_state("contact", form)
        return render_template("contact.html", title="Contact", form=form)

    if form.validate_on_submit():
        try:
            current_app.extensions["contact_logger"].info(
                "name=%s | email=%s | phone=%s | subject=%s | message=%s",
                form.name.data.strip(),
                form.email.data.strip(),
                form.phone.data.strip(),
                form.subject.data,
                form.message.data.strip(),
            )
            flash(
                f"Contact request from {form.name.data.strip()} ({form.email.data.strip()}) was saved.",
                "success",
            )
        except Exception:
            flash(
                "The form was submitted, but the log entry could not be saved.",
                "danger",
            )

        return redirect(url_for("contact"))

    stash_form_state("contact", form, exclude_fields={"submit"})
    flash("Please correct the errors in the contact form.", "danger")
    return redirect(url_for("contact"))


@dataclass(frozen=True)
class DemoUser:
    username: str
    password: str
    display_name: str


DEMO_USER = DemoUser(
    username="student",
    password="lab5pass",
    display_name="Demo Student",
)


def is_valid_identity(identity: str) -> bool:
    return identity == DEMO_USER.username


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if request.method == "GET":
        restore_form_state("login", form)
        return render_template(
            "login.html",
            title="Login",
            form=form,
            demo_user=DEMO_USER,
        )

    if form.validate_on_submit():
        username = form.username.data.strip()
        password = form.password.data

        if is_valid_identity(username) and password == DEMO_USER.password:
            session["username"] = username
            session["user_display_name"] = DEMO_USER.display_name

            flash(
                f"Signed in successfully as {DEMO_USER.display_name}",
                "success",
            )
            return redirect(url_for("login"))

        stash_form_state("login", form, exclude_fields={"password", "submit"})
        flash(
            "Authentication failed. Check your username/email and password.", "danger"
        )
        return redirect(url_for("login"))

    stash_form_state("login", form, exclude_fields={"password", "submit"})
    flash("Please correct the errors in the login form.", "danger")
    return redirect(url_for("login"))
