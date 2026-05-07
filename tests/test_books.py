from __future__ import annotations

from app import db
from app.books.models import Book, Genre
from app.models import User


def register(client, username="anna", email="anna@example.com", password="secret123"):
    return client.post(
        "/register",
        data={
            "username": username,
            "email": email,
            "password": password,
            "confirm_password": password,
        },
        follow_redirects=True,
    )


def login(client, email="anna@example.com", password="secret123"):
    return client.post(
        "/login",
        data={"email": email, "password": password, "remember_me": "y"},
        follow_redirects=True,
    )


def create_genre(name="Fantasy"):
    genre = Genre(name=name, shelf_code=f"{name[:3].upper()}-1", description=f"{name} books")
    db.session.add(genre)
    db.session.commit()
    return genre


def test_create_book_and_show_on_pages(client, app):
    register(client)

    with app.app_context():
        genre = create_genre()
        genre_id = genre.id

    response = client.post(
        "/books/create",
        data={
            "title": "The Hobbit",
            "author_name": "J. R. R. Tolkien",
            "publication_year": 1937,
            "isbn": "9780261103344",
            "description": "A classic fantasy novel about Bilbo Baggins, adventure, courage, and the journey to the Lonely Mountain.",
            "genre_id": genre_id,
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Book added successfully." in response.data
    assert b"The Hobbit" in response.data

    list_response = client.get("/books/")
    assert b"The Hobbit" in list_response.data

    with app.app_context():
        saved_book = Book.query.filter_by(title="The Hobbit").first()
        assert saved_book is not None
        assert saved_book.author.username == "anna"


def test_search_and_sort_books(client, app):
    with app.app_context():
        user = User(username="maria", email="maria@example.com")
        user.set_password("secret123")
        db.session.add(user)
        db.session.commit()

        genre = create_genre("Science fiction")
        db.session.add_all(
            [
                Book(
                    title="Dune",
                    author_name="Frank Herbert",
                    publication_year=1965,
                    isbn="9780441172719",
                    description="A detailed science fiction novel about politics, ecology, prophecy, and power on Arrakis.",
                    author=user,
                    genre=genre,
                ),
                Book(
                    title="Foundation",
                    author_name="Isaac Asimov",
                    publication_year=1951,
                    isbn="9780553293357",
                    description="A detailed classic about the collapse of empire and the attempt to preserve civilization through science.",
                    author=user,
                    genre=genre,
                ),
            ]
        )
        db.session.commit()

    response = client.get("/books/?q=Isaac&sort=author")

    assert response.status_code == 200
    assert b"Foundation" in response.data
    assert b"Dune" not in response.data


def test_only_owner_can_edit_or_delete_book(client, app):
    with app.app_context():
        owner = User(username="owner", email="owner@example.com")
        owner.set_password("secret123")
        intruder = User(username="guest", email="guest@example.com")
        intruder.set_password("secret123")
        db.session.add_all([owner, intruder])
        db.session.commit()

        genre = create_genre("Drama")
        book = Book(
            title="Hamlet",
            author_name="William Shakespeare",
            publication_year=1603,
            isbn="9780743477123",
            description="This book entry exists to verify that authorization rules are enforced correctly for owner-only actions.",
            author=owner,
            genre=genre,
        )
        db.session.add(book)
        db.session.commit()
        book_id = book.id

    login(client, email="guest@example.com")

    edit_response = client.post(
        f"/books/{book_id}/edit",
        data={
            "title": "Changed title",
            "author_name": "Unknown",
            "publication_year": 2000,
            "isbn": "1234567890",
            "description": "This should never be accepted because the current user does not own the book record in the system.",
            "genre_id": 1,
        },
    )
    delete_response = client.post(f"/books/{book_id}/delete")

    assert edit_response.status_code == 403
    assert delete_response.status_code == 403


def test_missing_book_returns_404(client):
    response = client.get("/books/999")
    assert response.status_code == 404


def test_create_book_validation_errors_are_shown(client, app):
    register(client, username="kate", email="kate@example.com")

    with app.app_context():
        genre = create_genre("History")
        genre_id = genre.id

    response = client.post(
        "/books/create",
        data={
            "title": "A",
            "author_name": "AB",
            "publication_year": 1400,
            "isbn": "123",
            "description": "too short",
            "genre_id": genre_id,
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Field must be between 2 and 160 characters long." in response.data
    assert b"Field must be between 3 and 120 characters long." in response.data
    assert b"Number must be between 1450 and 2100." in response.data
    assert b"Field must be between 10 and 20 characters long." in response.data
    assert b"Field must be between 30 and 5000 characters long." in response.data


def test_account_route_requires_login_and_displays_current_user(client):
    redirect_response = client.get("/account")
    assert redirect_response.status_code == 302
    assert "/login" in redirect_response.headers["Location"]

    register(client, username="nina", email="nina@example.com")
    response = client.get("/account")

    assert response.status_code == 200
    assert b"Account" in response.data
    assert b"nina@example.com" in response.data
