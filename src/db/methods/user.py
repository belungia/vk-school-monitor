import logging

from sqlalchemy import distinct, func, insert, or_, select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert

from src.db.session import get_db_session
from src.db.models import User, Post


logger = logging.getLogger(__name__)


async def api_add_users(users_data: list[dict]) -> int:
    if not users_data:
        return 0

    async with get_db_session() as session:
        try:
            stmt = pg_insert(User).values(users_data).on_conflict_do_nothing(index_elements=["link"])
            result = await session.execute(stmt)
            await session.commit()
            return result.rowcount
        
        except Exception as e:
            logger.error(f"Unexpected db error for add user(s): {e}")
            if session:
                await session.rollback()
            raise

async def get_tracked_users_last_post_dates() -> dict[int, int | None]:
    try:
        async with get_db_session() as session:
            stmt = select(User.id, User.last_post_date).where(User.status_id == 1)
            result = await session.execute(stmt)
            return {row[0]: row[1] for row in result.all()}
            
    except Exception as e:
        logger.error(f"Unexpected error, failed to get last post dates for tracked users: {e}")
        if session:
            await session.rollback()
        raise

async def update_last_post_dates():
        try:
            async with get_db_session() as session:
                max_date_subq = (
                    select(func.max(Post.date))
                    .where(Post.user_id == User.id)
                    .correlate(User)               
                    .scalar_subquery()
                )

                stmt = (
                    update(User)
                    .where(User.id.in_(select(distinct(Post.user_id))))
                    .values(last_post_date=max_date_subq)
                )

                await session.execute(stmt)
                await session.commit()

        except Exception as e:
            logger.error(f"Unexpected error while update last_post_date: {e}")
            if session:
                await session.rollback()
            raise

async def api_get_users(search: str = None, monitoring: int = None):
    try:
        async with get_db_session() as session:
            stmt = select(
                User.id,
                User.name,
                User.surname,
                User.phone,
                User.link,
                User.status_id,
                User.last_post_date
            )
            
            if search:
                search_term = f"%{search}%"
                stmt = stmt.where(
                    or_(
                        User.name.ilike(search_term),
                        User.surname.ilike(search_term)
                    )
                )
            
            if monitoring is not None:
                stmt = stmt.where(User.status_id == monitoring)

            result = await session.execute(stmt)

            return result.mappings().all()

    except Exception as e:
        logger.error(f"Unexpected db error for get users: {e}")
        if session:
            await session.rollback()
        raise

async def api_update_user_status(user_id: int, status_id: int):
    try:
        async with get_db_session() as session:
            user = await session.get(User, user_id)
            if not user:
                raise ValueError(f"User with id {user_id} not found")

            if status_id not in (0, 1):
                raise ValueError(f"status_id must be 0 or 1")

            user.status_id = status_id
            await session.commit()

            return {
                "id": user.id,
                "status_id": user.status_id
            }
        
    except Exception as e:
        logger.error(f"Unexpected error for update user status: {e}")
        if session:
            await session.rollback()
        raise