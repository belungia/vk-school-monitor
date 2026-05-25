from datetime import datetime
from typing import Optional
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.mixins import CreatedAtMixin, UpdatedAtMixin
from src.db.models import Base


if TYPE_CHECKING:
    from src.db.models.post import Post
    from src.db.models.user import User


class Group(Base):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    link: Mapped[str] = mapped_column(String(255), unique=True) 
    status_id: Mapped[int] = mapped_column(ForeignKey("group_statuses.id"), index=True, default=0)
    last_post_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=False), default=None)

    status: Mapped["GroupStatus"] = relationship("GroupStatus", back_populates="groups")
    members: Mapped[list["UserGroup"]] = relationship("UserGroup", back_populates="group")
    posts: Mapped[list["Post"]] = relationship("Post", back_populates="group")


class GroupStatus(Base):
    __tablename__ = "group_statuses"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    status: Mapped[str] = mapped_column(String(30), unique=True)

    groups: Mapped[list["Group"]] = relationship("Group", back_populates="status")


class UserGroup(Base):
    __tablename__ = "user_groups"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), primary_key=True)

    user: Mapped["User"] = relationship("User", back_populates="subscriptions")
    group: Mapped["Group"] = relationship("Group", back_populates="members")