from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.models.base import Base


if TYPE_CHECKING:
    from src.db.models.user import User
    from src.db.models.alert import Alert
    from src.db.models.group import Group


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    group_id: Mapped[Optional[int]] = mapped_column(ForeignKey("groups.id"))
    link: Mapped[str] = mapped_column(String(255), unique=True)
    text: Mapped[Optional[str]] = mapped_column(Text)
    date: Mapped[datetime] = mapped_column(DateTime, index=True)
    status_id: Mapped[int] = mapped_column(ForeignKey("post_statuses.id"), index=True, default=0)

    status: Mapped["PostStatus"] = relationship("PostStatus", back_populates="posts")
    user: Mapped["User"] = relationship("User", back_populates="posts")
    group: Mapped[Optional["Group"]] = relationship("Group", back_populates="posts")
    alert: Mapped["Alert"] = relationship("Alert", back_populates="post", uselist=False, cascade="all, delete-orphan")
        

class PostStatus(Base):
    __tablename__ = "post_statuses"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    status: Mapped[str] = mapped_column(String(30), unique=True)

    posts: Mapped[list["Post"]] = relationship("Post", back_populates="status")