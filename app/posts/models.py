from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum

from sqlalchemy import DateTime, Enum as SqlEnum, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .. import db


def utcnow() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


class PostCategory(str, Enum):
    NEWS = "news"
    PUBLICATION = "publication"
    TECH = "tech"
    OTHER = "other"


class Post(db.Model):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    posted: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)
    category: Mapped[PostCategory] = mapped_column(
        SqlEnum(PostCategory, name="post_category"),
        default=PostCategory.OTHER,
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    author: Mapped[str] = mapped_column(String(20), default="Anonymous", nullable=False)

    def __repr__(self) -> str:
        return f"<Post id={self.id} title={self.title!r}>"
