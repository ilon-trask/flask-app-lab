from flask_wtf import FlaskForm
from wtforms import (
    PasswordField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import DataRequired, Length, Optional, Regexp

CONTACT_SUBJECT_CHOICES = [
    ("", "Choose a subject"),
    ("partnership", "Partnership"),
    ("support", "Support request"),
    ("feedback", "Feedback"),
    ("career", "Career opportunity"),
]

EMAIL_PATTERN = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
PHONE_PATTERN = r"^\+380\d{9}$"


class ContactForm(FlaskForm):
    name = StringField(
        "Name",
        validators=[
            DataRequired(message="Name is required."),
            Length(
                min=4,
                max=10,
                message="Name must be between 4 and 10 characters long.",
            ),
        ],
    )
    email = StringField(
        "Email",
        validators=[
            DataRequired(message="Email is required."),
            Regexp(EMAIL_PATTERN, message="Enter a valid email address."),
        ],
    )
    phone = StringField(
        "Phone",
        validators=[
            Optional(),
            Regexp(PHONE_PATTERN, message="Phone must use the +380XXXXXXXXX format."),
        ],
        description="Optional, but if provided it must match +380XXXXXXXXX.",
    )
    subject = SelectField(
        "Subject",
        choices=CONTACT_SUBJECT_CHOICES,
        validators=[DataRequired(message="Choose a subject.")],
    )
    message = TextAreaField(
        "Message",
        validators=[
            DataRequired(message="Message is required."),
            Length(max=500, message="Message must be 500 characters or fewer."),
        ],
    )
    submit = SubmitField("Send message")


class LoginForm(FlaskForm):
    username = StringField(
        "Username or email",
        validators=[DataRequired(message="Username or email is required.")],
    )
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(message="Password is required."),
            Length(
                min=4,
                max=10,
                message="Password must be between 4 and 10 characters long.",
            ),
        ],
    )
    submit = SubmitField("Sign in")
