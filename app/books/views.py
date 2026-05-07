from __future__ import annotations

from sqlalchemy import or_

from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app import db
from app.books import books_bp
from app.books.forms import BookForm, SearchForm
from app.books.models import Book, Genre


def populate_genre_choices(form: BookForm) -> bool:
    genres = Genre.query.order_by(Genre.name.asc()).all()
    form.genre_id.choices = [(genre.id, genre.name) for genre in genres]
    return bool(genres)


def get_owned_book_or_404(book_id: int) -> Book:
    book = db.session.get(Book, book_id)
    if book is None:
        abort(404)
    if book.user_id != current_user.id:
        abort(403)
    return book


@books_bp.route("/", methods=["GET"])
def list_books():
    form = SearchForm(request.args, meta={"csrf": False})
    books_query = Book.query.join(Genre)

    search_value = (form.q.data or "").strip()
    sort_value = form.sort.data or "newest"

    if search_value:
        books_query = books_query.filter(
            or_(
                Book.title.ilike(f"%{search_value}%"),
                Book.author_name.ilike(f"%{search_value}%"),
            )
        )

    if sort_value == "oldest":
        books_query = books_query.order_by(Book.created_at.asc())
    elif sort_value == "title":
        books_query = books_query.order_by(Book.title.asc())
    elif sort_value == "author":
        books_query = books_query.order_by(Book.author_name.asc(), Book.title.asc())
    elif sort_value == "genre":
        books_query = books_query.order_by(Genre.name.asc(), Book.title.asc())
    elif sort_value == "year":
        books_query = books_query.order_by(
            Book.publication_year.desc(), Book.title.asc()
        )
    else:
        books_query = books_query.order_by(Book.created_at.desc())
        sort_value = "newest"

    form.sort.data = sort_value
    books = books_query.all()
    return render_template("books/books.html", books=books, search_form=form)


@books_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_book():
    form = BookForm()
    if not populate_genre_choices(form):
        flash(
            "Please add genres first using flask shell before creating books. Command provided in README",
            "warning",
        )
        return redirect(url_for("books.list_books"))

    if form.validate_on_submit():
        book = Book(
            title=form.title.data.strip(),
            author_name=form.author_name.data.strip(),
            publication_year=form.publication_year.data,
            isbn=form.isbn.data.strip(),
            description=form.description.data.strip(),
            genre_id=form.genre_id.data,
            author=current_user,
        )
        db.session.add(book)
        db.session.commit()
        flash("Book added successfully.", "success")
        return redirect(url_for("books.book_detail", book_id=book.id))

    return render_template("books/add_book.html", form=form, page_title="Add Book")


@books_bp.route("/<int:book_id>")
def book_detail(book_id: int):
    book = db.session.get(Book, book_id)
    if book is None:
        abort(404)
    return render_template("books/detail_book.html", book=book)


@books_bp.route("/<int:book_id>/edit", methods=["GET", "POST"])
@login_required
def edit_book(book_id: int):
    book = get_owned_book_or_404(book_id)
    form = BookForm(obj=book)
    populate_genre_choices(form)

    if form.validate_on_submit():
        book.title = form.title.data.strip()
        book.author_name = form.author_name.data.strip()
        book.publication_year = form.publication_year.data
        book.isbn = form.isbn.data.strip()
        book.description = form.description.data.strip()
        book.genre_id = form.genre_id.data
        db.session.commit()
        flash("Book updated successfully.", "success")
        return redirect(url_for("books.book_detail", book_id=book.id))

    return render_template("books/add_book.html", form=form, page_title="Edit Book")


@books_bp.post("/<int:book_id>/delete")
@login_required
def delete_book(book_id: int):
    book = get_owned_book_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    flash("Book deleted successfully.", "success")
    return redirect(url_for("books.list_books"))
