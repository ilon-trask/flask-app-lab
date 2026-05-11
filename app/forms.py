from flask_wtf import FlaskForm

from wtforms import (
    StringField,
    PasswordField,
    SubmitField,
    TextAreaField,
    DateTimeLocalField,
    SelectField,
    SelectMultipleField,
)

from wtforms.validators import DataRequired, Email, Length

from datetime import datetime
from .models import PostCategory, User, Tag


class RegisterForm(FlaskForm):

    username = StringField(
        "Username", validators=[DataRequired(), Length(min=3, max=30)]
    )

    email = StringField("Email", validators=[DataRequired(), Email()])

    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])

    submit = SubmitField("Register")


class PostForm(FlaskForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.author_id.choices = [
            (a.id, a.username) for a in User.query.order_by(User.id)
        ]
        self.tags.choices = [(a.id, a.name) for a in Tag.query.order_by(Tag.id)]

    title = StringField("Title", validators=[DataRequired()])
    content = TextAreaField("Content", validators=[DataRequired()])
    publish_date = DateTimeLocalField(
        "Publish date",
        validators=[DataRequired()],
        default=datetime.now,
        format="%Y-%m-%dT%H:%M",
    )
    category = SelectField(
        "Category",
        validators=[DataRequired()],
        choices=[(category.value, category.value.title()) for category in PostCategory],
        default=PostCategory.TECH.value,
    )
    author_id = SelectField("Author", validators=[DataRequired()], coerce=int)
    tags = SelectMultipleField("Tags", coerce=int)
    add_post = SubmitField("Add Post")
