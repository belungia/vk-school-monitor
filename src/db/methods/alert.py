import logging

from sqlalchemy import insert, or_, select
from sqlalchemy.dialects.postgresql import insert as pg_insert

from src.db.models import User, Post
from src.db.models.alert import Alert
from src.db.session import get_db_session


logger = logging.getLogger(__name__)


async def add_alerts(analyzed_posts: list[dict]):
    if not analyzed_posts:
        return
    try:
        async with get_db_session() as session:
            stmt = pg_insert(Alert).values(analyzed_posts).on_conflict_do_nothing(
                index_elements=["user_id", "post_id"]
            )
            await session.execute(stmt)
            await session.commit()
    except Exception as e:
        logger.error(f"Unexpected error for add alerts: {e}")
        if session:
            await session.rollback()
        raise

async def api_get_alerts(search: str = None):
    try:
        async with get_db_session() as session:
            stmt = select(
                Alert.id,
                User.name,
                User.surname,
                Post.link,
                Alert.reason
            ).join(User, Alert.user_id == User.id) \
             .join(Post, Alert.post_id == Post.id)
            
            if search:
                search_term = f"%{search}%"
                stmt = stmt.where(
                    or_(
                        User.name.ilike(search_term),
                        User.surname.ilike(search_term),
                        Alert.reason.ilike(search_term)
                    )
                )
            
            result = await session.execute(stmt)
            rows = result.mappings().all()

            return [
                {
                    "id": row["id"],
                    "studentName": f"{row['name'] or ''} {row['surname'] or ''}".strip(),
                    "postLink": row["link"],
                    "reason": row["reason"]
                }
                for row in rows
            ]

    except Exception as e:
        logger.error(f"Unexpected error for get alerts: {e}")
        if session:
            await session.rollback()
        raise