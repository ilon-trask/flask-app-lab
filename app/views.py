from __future__ import annotations

from urllib.parse import urlsplit

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app import app, db
from app.forms import LoginForm, RegisterForm
from app.models import User
from app.posts.models import Post, Tag


@app.route("/")
def index():
    return redirect(url_for("posts.list_posts"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("account"))

    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data.strip(),
            email=form.email.data.strip().lower(),
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Реєстрація успішна. Тепер увійдіть у систему.", "success")
        return redirect(url_for("login"))

    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("account"))

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        user = db.session.execute(
            db.select(User).where(User.email == email)
        ).scalar_one_or_none()

        if user is None or not user.check_password(form.password.data):
            flash("Неправильна електронна пошта або пароль.", "danger")
            return render_template("login.html", form=form)

        login_user(user, remember=form.remember.data)
        flash(f"Вітаємо, {user.username}!", "success")
        next_page = request.args.get("next")
        if next_page and urlsplit(next_page).netloc == "":
            return redirect(next_page)
        return redirect(url_for("account"))

    return render_template("login.html", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Ви вийшли з акаунта.", "success")
    return redirect(url_for("login"))


@app.route("/account")
@login_required
def account():
    return render_template("account.html")


@app.route("/users")
def users_list():
    users = list(
        db.session.execute(db.select(User).order_by(User.username.asc(), User.id.asc())).scalars()
    )
    return render_template("users.html", users=users, users_count=len(users))


@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404


@app.errorhandler(403)
def permission_denied(error):
    return render_template("403.html"), 403


@app.shell_context_processor
def make_shell_context():
    return {
        "db": db,
        "User": User,
        "Post": Post,
        "Tag": Tag,
    }
