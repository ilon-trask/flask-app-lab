from __future__ import annotations

from flask_wtf import FlaskForm
from wtforms import SelectField, SelectMultipleField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length

from app import db
from app.models import User
from app.posts.models import Tag


class PostForm(FlaskForm):
    title = StringField("Заголовок", validators=[DataRequired(), Length(max=200)])
    content = TextAreaField("Текст поста", validators=[DataRequired()])
    author_id = SelectField("Автор", coerce=int, validators=[DataRequired()])
    tags = SelectMultipleField("Теги", coerce=int)
    submit = SubmitField("Зберегти")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.author_id.choices = [
            (author.id, author.username)
            for author in db.session.execute(
                db.select(User).order_by(User.id)
            ).scalars()
        ]
        self.tags.choices = [
            (tag.id, tag.name)
            for tag in db.session.execute(
                db.select(Tag).order_by(Tag.name)
            ).scalars()
        ]
