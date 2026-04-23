from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from flask_login import UserMixin
from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.security import check_password_hash, generate_password_hash

from app import db, login_manager

if TYPE_CHECKING:
    from app.posts.models import Post


@login_manager.user_loader
def load_user(user_id: str) -> User | None:
    return db.session.get(User, int(user_id))


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    image: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
        default="profile_default.jpg",
    )
    about_me: Mapped[str | None] = mapped_column(Text, nullable=True, default="")
    last_seen: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        default=lambda: datetime.now(UTC),
    )
    posts: Mapped[list["Post"]] = relationship(
        back_populates="author",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        if self.password_hash == password:
            return True
        try:
            return check_password_hash(self.password_hash, password)
        except ValueError:
            return False

    def __repr__(self) -> str:
        return f"<User {self.username}>"
