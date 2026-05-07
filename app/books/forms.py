from __future__ import annotations

from flask_wtf import FlaskForm
from wtforms import IntegerField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, NumberRange


class SearchForm(FlaskForm):
    q = StringField("Search by title or author", validators=[Length(max=160)])
    sort = SelectField(
        "Sort by",
        choices=[
            ("newest", "Newest first"),
            ("oldest", "Oldest first"),
            ("title", "Title A-Z"),
            ("author", "Author A-Z"),
            ("genre", "Genre"),
            ("year", "Publication year"),
        ],
    )
    submit = SubmitField("Apply")


class BookForm(FlaskForm):
    title = StringField(
        "Title",
        validators=[DataRequired(), Length(min=2, max=160)],
    )
    author_name = StringField(
        "Author",
        validators=[DataRequired(), Length(min=3, max=120)],
    )
    publication_year = IntegerField(
        "Publication year",
        validators=[DataRequired(), NumberRange(min=1450, max=2100)],
    )
    isbn = StringField(
        "ISBN",
        validators=[DataRequired(), Length(min=10, max=20)],
    )
    description = TextAreaField(
        "Description",
        validators=[DataRequired(), Length(min=30, max=5000)],
    )
    genre_id = SelectField(
        "Genre",
        coerce=int,
        validators=[DataRequired(message="Please choose a genre.")],
    )
    submit = SubmitField("Save book")
