from __future__ import annotations

import secrets
from datetime import UTC, datetime
from pathlib import Path

from flask import current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.utils import secure_filename

from app import app, db
from app.forms import ChangePasswordForm, LoginForm, RegistrationForm, UpdateAccountForm
from app.models import User
from app.posts.models import Post, Tag


@app.route("/")
def index():
    return redirect(url_for("posts.list_posts"))


@app.before_request
def update_last_seen():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(UTC)
        db.session.commit()


@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("account"))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data.strip(),
            email=form.email.data.strip().lower(),
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Реєстрація пройшла успішно. Тепер можна увійти.", "success")
        return redirect(url_for("login"))

    return render_template("auth/register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("account"))

    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.execute(
            db.select(User).where(User.email == form.email.data.strip().lower())
        ).scalar_one_or_none()

        if user is None or not user.check_password(form.password.data):
            flash("Неправильний email або пароль.", "danger")
        else:
            if user.password_hash == form.password.data:
                user.set_password(form.password.data)
                db.session.commit()
            login_user(user)
            flash("Вхід виконано успішно.", "success")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("account"))

    return render_template("auth/login.html", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Ви вийшли з акаунта.", "success")
    return redirect(url_for("login"))


@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    account_form = UpdateAccountForm(prefix="account")
    password_form = ChangePasswordForm(prefix="password")

    if request.method == "GET":
        account_form.username.data = current_user.username
        account_form.email.data = current_user.email
        account_form.about_me.data = current_user.about_me

    if account_form.submit.name in request.form and account_form.validate():
        current_user.username = account_form.username.data.strip()
        current_user.email = account_form.email.data.strip().lower()
        current_user.about_me = (account_form.about_me.data or "").strip()

        if account_form.image.data:
            current_user.image = save_picture(account_form.image.data)

        db.session.commit()
        flash("Профіль оновлено.", "success")
        return redirect(url_for("account"))

    if password_form.submit.name in request.form and password_form.validate():
        current_user.set_password(password_form.new_password.data)
        db.session.commit()
        flash("Пароль успішно змінено.", "success")
        return redirect(url_for("account"))

    image_url = url_for("static", filename=f"profile_pics/{current_user.image}")
    return render_template(
        "account.html",
        account_form=account_form,
        password_form=password_form,
        image_url=image_url,
    )


@app.shell_context_processor
def make_shell_context():
    return {
        "db": db,
        "User": User,
        "Post": Post,
        "Tag": Tag,
    }


@app.context_processor
def inject_current_user():
    return {"current_user": current_user}


def save_picture(uploaded_file) -> str:
    random_hex = secrets.token_hex(8)
    filename = secure_filename(uploaded_file.filename or "profile.jpg")
    extension = Path(filename).suffix.lower() or ".jpg"
    picture_name = f"{random_hex}{extension}"
    picture_path = Path(current_app.config["PROFILE_PICS_FOLDER"]) / picture_name
    uploaded_file.save(picture_path)
    return picture_name
