from __future__ import annotations

from flask_wtf import FlaskForm
from wtforms import SelectMultipleField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length

from app import db
from app.posts.models import Tag


class PostForm(FlaskForm):
    title = StringField("Заголовок", validators=[DataRequired(), Length(max=200)])
    content = TextAreaField("Текст поста", validators=[DataRequired()])
    tags = SelectMultipleField("Теги", coerce=int)
    submit = SubmitField("Зберегти пост")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tags.choices = [
            (tag.id, tag.name)
            for tag in db.session.execute(
                db.select(Tag).order_by(Tag.name)
            ).scalars()
        ]
