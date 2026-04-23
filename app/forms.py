from __future__ import annotations

from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import PasswordField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, EqualTo, Length, ValidationError

from app import db
from flask_login import current_user
from app.models import User


class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(max=64)])
    email = StringField("Email", validators=[DataRequired(), Length(max=120)])
    password = PasswordField("Пароль", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField(
        "Підтвердження пароля",
        validators=[DataRequired(), EqualTo("password")],
    )
    submit = SubmitField("Зареєструватися")

    def validate_username(self, username: StringField) -> None:
        user = db.session.execute(
            db.select(User).where(User.username == username.data.strip())
        ).scalar_one_or_none()
        if user is not None:
            raise ValidationError("Користувач з таким username вже існує.")

    def validate_email(self, email: StringField) -> None:
        user = db.session.execute(
            db.select(User).where(User.email == email.data.strip().lower())
        ).scalar_one_or_none()
        if user is not None:
            raise ValidationError("Користувач з таким email вже існує.")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Length(max=120)])
    password = PasswordField("Пароль", validators=[DataRequired()])
    submit = SubmitField("Увійти")


class UpdateAccountForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(max=64)])
    email = StringField("Email", validators=[DataRequired(), Length(max=120)])
    about_me = TextAreaField("Про себе", validators=[Length(max=500)])
    image = FileField(
        "Update Profile Picture",
        validators=[FileAllowed(["jpg", "png", "jpeg"])],
    )
    submit = SubmitField("Оновити профіль")

    def validate_username(self, username: StringField) -> None:
        new_value = username.data.strip()
        if current_user.is_authenticated and new_value == current_user.username:
            return

        user = db.session.execute(
            db.select(User).where(User.username == new_value)
        ).scalar_one_or_none()
        if user is not None:
            raise ValidationError("Такий username вже використовується.")

    def validate_email(self, email: StringField) -> None:
        new_value = email.data.strip().lower()
        if current_user.is_authenticated and new_value == current_user.email:
            return

        user = db.session.execute(
            db.select(User).where(User.email == new_value)
        ).scalar_one_or_none()
        if user is not None:
            raise ValidationError("Такий email вже використовується.")


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField("Поточний пароль", validators=[DataRequired()])
    new_password = PasswordField(
        "Новий пароль",
        validators=[DataRequired(), Length(min=6)],
    )
    confirm_new_password = PasswordField(
        "Підтвердження нового пароля",
        validators=[DataRequired(), EqualTo("new_password")],
    )
    submit = SubmitField("Змінити пароль")

    def validate_current_password(self, current_password: PasswordField) -> None:
        if current_user.is_authenticated and not current_user.check_password(
            current_password.data
        ):
            raise ValidationError("Поточний пароль введено неправильно.")
