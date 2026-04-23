from __future__ import annotations

from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length, ValidationError

from app import db
from app.models import User


class RegisterForm(FlaskForm):
    username = StringField(
        "Ім'я користувача",
        validators=[DataRequired(), Length(min=3, max=64)],
    )
    email = StringField(
        "Електронна пошта",
        validators=[DataRequired(), Length(min=5, max=120)],
    )
    password = PasswordField(
        "Пароль",
        validators=[DataRequired(), Length(min=6, max=128)],
    )
    confirm_password = PasswordField(
        "Підтвердження пароля",
        validators=[
            DataRequired(),
            EqualTo("password", message="Паролі мають збігатися."),
        ],
    )
    submit = SubmitField("Зареєструватися")

    def validate_username(self, field: StringField) -> None:
        user = db.session.execute(
            db.select(User).where(User.username == field.data.strip())
        ).scalar_one_or_none()
        if user is not None:
            raise ValidationError("Користувач з таким ім'ям уже існує.")

    def validate_email(self, field: StringField) -> None:
        email = field.data.strip().lower()
        if "@" not in email or "." not in email:
            raise ValidationError("Введіть коректну електронну пошту.")

        user = db.session.execute(
            db.select(User).where(User.email == email)
        ).scalar_one_or_none()
        if user is not None:
            raise ValidationError("Користувач з такою поштою вже існує.")


class LoginForm(FlaskForm):
    email = StringField(
        "Електронна пошта",
        validators=[DataRequired(), Length(min=5, max=120)],
    )
    password = PasswordField(
        "Пароль",
        validators=[DataRequired(), Length(min=6, max=128)],
    )
    remember = BooleanField("Запам'ятати мене")
    submit = SubmitField("Увійти")
