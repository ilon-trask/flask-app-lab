from __future__ import annotations

from datetime import UTC, datetime

from app import db


class Genre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    shelf_code = db.Column(db.String(20), nullable=False)
    description = db.Column(db.String(180), nullable=False)
    books = db.relationship("Book", back_populates="genre")

    def __repr__(self) -> str:
        return f"<Genre {self.name}>"


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(160), nullable=False)
    author_name = db.Column(db.String(120), nullable=False)
    publication_year = db.Column(db.Integer, nullable=False)
    isbn = db.Column(db.String(20), nullable=False)
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"), nullable=False)

    author = db.relationship("User", back_populates="books")
    genre = db.relationship("Genre", back_populates="books")

    def __repr__(self) -> str:
        return f"<Book {self.title}>"
