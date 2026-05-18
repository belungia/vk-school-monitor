import logging

from sqlalchemy import insert

from src.db.models.alert import Alert
from src.db.session import get_db_session


logger = logging.getLogger(__name__)


async def add_alerts(analyzed_posts: list[dict]):
    try:
        async with get_db_session() as session:
            await session.execute(insert(Alert).values((analyzed_posts)))
    
    except Exception as e:
        raise