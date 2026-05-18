import logging

from sqlalchemy import and_, insert, null, select, update

from src.db.models.post import Post
from src.db.session import get_db_session 


logger = logging.getLogger(__name__)


async def add_posts(posts: list[dict]):
    try:
        async with get_db_session() as session:
            await session.execute(insert(Post).values(posts))
            await session.commit()
            return True
        
    except Exception as e:
        logger.error(f"Unexpected db error for add posts: {e}")
        if session:
            await session.rollback()
        raise
    
async def get_unanalyzed_posts():
    try:
        async with get_db_session() as session:
            stmt = select(Post.id, Post.user_id, Post.text).where(and_(Post.text != '', Post.status_id == 0))
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
            stmt = (
                update(Post)
                .where(Post.id.in_(ids), Post.status_id == 0)
                .values(status_id=1)
            )
            await session.execute(stmt)
            await session.commit()

    except Exception as e:
        logger.error(f"Unexpected db error for update statuses for posts: {e}")
        if session:
            await session.rollback()
        raise