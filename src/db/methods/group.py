import logging
from datetime import datetime
from typing import Optional

from sqlalchemy import select, func, distinct, update, insert, and_
from sqlalchemy.dialects.postgresql import insert as pg_insert

from src.db.models.group import Group, GroupStatus, UserGroup
from src.db.models.post import Post
from src.db.models.user import User
from src.db.session import get_db_session

logger = logging.getLogger(__name__)


async def add_groups(groups_data: list[dict]) -> int:
    if not groups_data:
        return 0

    async with get_db_session() as session:
        try:
            stmt = pg_insert(Group).values(groups_data).on_conflict_do_nothing(index_elements=["link"])
            result = await session.execute(stmt)
            await session.commit()
            return result.rowcount
        except Exception as e:
            logger.error(f"Error adding groups: {e}")
            await session.rollback()
            raise


async def add_user_groups(subscriptions: list[dict]) -> int:
    if not subscriptions:
        return 0

    async with get_db_session() as session:
        try:
            stmt = pg_insert(UserGroup).values(subscriptions).on_conflict_do_nothing(
                index_elements=["user_id", "group_id"]
            )
            result = await session.execute(stmt)
            await session.commit()
            return result.rowcount
        except Exception as e:
            logger.error(f"Error adding user-group subscriptions: {e}")
            await session.rollback()
            raise


async def get_monitored_groups_last_post_dates() -> dict[int, Optional[datetime]]:
    try:
        async with get_db_session() as session:
            stmt = select(Group.id, Group.last_post_date).where(Group.status_id == 1)
            result = await session.execute(stmt)
            return {row[0]: row[1] for row in result.all()}
    except Exception as e:
        logger.error(f"Failed to get last post dates for monitored groups: {e}")
        raise
    
async def api_get_groups(search: str = None, monitoring: int = None) -> list[dict]:
    async with get_db_session() as session:
        stmt = select(
            Group.id,
            Group.name,
            Group.link,
            Group.status_id,
            Group.last_post_date
        )
        if search:
            stmt = stmt.where(Group.name.ilike(f"%{search}%"))
        if monitoring is not None:
            stmt = stmt.where(Group.status_id == monitoring)
        result = await session.execute(stmt)
        rows = result.mappings().all()
        return [dict(r) for r in rows]

async def api_update_group_status(group_id: int, status_id: int):
    async with get_db_session() as session:
        group = await session.get(Group, group_id)
        if not group:
            raise ValueError(f"Group with id {group_id} not found")
        if status_id not in (0, 1):
            raise ValueError("status_id must be 0 or 1")
        group.status_id = status_id
        await session.commit()
        return {"id": group.id, "status_id": group.status_id}

async def update_group_last_post_dates():
    async with get_db_session() as session:
        try:
            max_date_subq = (
                select(func.max(Post.date))
                .where(Post.group_id == Group.id)
                .correlate(Group)
                .scalar_subquery()
            )

            stmt = (
                update(Group)
                .where(Group.id.in_(select(distinct(Post.group_id))))
                .values(last_post_date=max_date_subq)
            )
            await session.execute(stmt)
            await session.commit()
        except Exception as e:
            logger.error(f"Error updating group last_post_date: {e}")
            await session.rollback()
            raise

async def get_subscribed_users(group_id: int) -> list[int]:
    async with get_db_session() as session:
        stmt = (
            select(UserGroup.user_id)
            .join(User, UserGroup.user_id == User.id)
            .where(UserGroup.group_id == group_id, User.status_id == 1)
        )
        result = await session.execute(stmt)
        return [row[0] for row in result.all()]