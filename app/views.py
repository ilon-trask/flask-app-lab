from __future__ import annotations

from flask import flash, redirect, render_template, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app import app, db
from app.forms import LoginForm, RegisterForm
from app.models import User


@app.route("/")
def index():
    from app.books.models import Book

    latest_books = Book.query.order_by(Book.created_at.desc()).limit(3).all()
    return render_template("index.html", latest_books=latest_books)


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("books.list_books"))

    form = RegisterForm()
    if form.validate_on_submit():
        existing_user = User.query.filter(
            (User.username == form.username.data.strip())
            | (User.email == form.email.data.strip().lower())
        ).first()
        if existing_user:
            flash("A user with this username or email already exists.", "danger")
        else:
            user = User(
                username=form.username.data.strip(),
                email=form.email.data.strip().lower(),
            )
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            flash("Welcome! Your account has been created.", "success")
            return redirect(url_for("books.list_books"))

    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("books.list_books"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.strip().lower()).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            flash("You are logged in.", "success")
            return redirect(url_for("books.list_books"))
        flash("Invalid email or password.", "danger")

    return render_template("login.html", form=form)


@app.route("/account")
@login_required
def account():
    return render_template("account.html")


@app.post("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))


@app.errorhandler(403)
def forbidden(error):
    return render_template("403.html"), 403


@app.errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404
