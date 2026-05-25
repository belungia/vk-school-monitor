import logging

from sqlalchemy import and_, insert, null, select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert

from src.db.models.post import Post
from src.db.session import get_db_session 


logger = logging.getLogger(__name__)


async def add_posts(posts: list[dict]) -> int:
    if not posts:
        return 0
    async with get_db_session() as session:
        try:
            stmt = pg_insert(Post).values(posts).on_conflict_do_nothing(index_elements=["link"])
            result = await session.execute(stmt)
            await session.commit()
            return result.rowcount
        except Exception as e:
            logger.error(f"Unexpected db error for add posts: {e}")
            await session.rollback()
            raise
    
async def get_unanalyzed_posts():
    try:
        async with get_db_session() as session:
            stmt = select(Post.id, Post.user_id, Post.group_id, Post.text).where(and_(Post.text != '', Post.status_id == 0))
            result = await session.execute(stmt)
            return result.all()

    except Exception as e:
        logger.error(f"Unexpected db error for get unanalyzed posts: {e}")
        if session:
            await session.rollback()
        raise

async def update_statuses(ids: list[int]):
    try:
        async with get_db_session() as session:
            if ids:
                stmt1 = (
                    update(Post)
                    .where(Post.id.in_(ids), Post.status_id == 0)
                    .values(status_id=1)
                )
                await session.execute(stmt1)

            stmt2 = (
                update(Post)
                .where(Post.text == '')
                .values(status_id=1)
            )
            await session.execute(stmt2)
            await session.commit()

    except Exception as e:
        logger.error(f"Unexpected db error for update statuses for posts: {e}")
        if session:
            await session.rollback()
        raise