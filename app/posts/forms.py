from __future__ import annotations

from flask_wtf import FlaskForm
from wtforms import BooleanField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.fields import DateTimeLocalField
from wtforms.validators import DataRequired, Length, Optional

from .models import utcnow
from .models import PostCategory


class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(max=150)])
    content = TextAreaField("Content", validators=[DataRequired(), Length(min=10)])
    enabled = BooleanField("Visible on site", default=True)
    publish_date = DateTimeLocalField(
        "Publish date",
        format="%Y-%m-%dT%H:%M",
        validators=[Optional()],
        default=utcnow,
    )
    category = SelectField(
        "Category",
        choices=[(category.value, category.value.title()) for category in PostCategory],
        validators=[DataRequired()],
        default=PostCategory.OTHER.value,
    )
    submit = SubmitField("Save Post")
