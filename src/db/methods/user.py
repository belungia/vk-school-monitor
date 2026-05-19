import logging

from sqlalchemy import insert, or_, select

from src.db.session import get_db_session
from src.db.models import User


logger = logging.getLogger(__name__)


async def api_add_user(
    id: int,
    link: str,
    name: str = None,
    surname: str = None,
    phone: str = None
):
    session = None
    try:
        async with get_db_session() as session:
            new_user = User(
                id=id,
                link=link,
                name=name,
                surname=surname,
                phone=phone
            )
            session.add(new_user)
            await session.commit()
            return True

    except Exception as e:
        logger.error(f"Unexpected db error for user {id}: {e}")
        if session:
            await session.rollback()
        raise

async def api_add_users(users_data: list[tuple]):
    session = None
    try: 
        async with get_db_session() as session:
            mappings = []
            for user_data in users_data:
                id, link, name, surname, phone = user_data
                mapping = {
                    "id": id,
                    "link": link,
                    "name": name,
                    "surname": surname,
                    "phone": phone
                }
                mappings.append(mapping)

            await session.execute(insert(User).values(mappings))
            await session.commit()
            return True
        
    except Exception as e:
        logger.error(f"Unexpected db error for batch add users: {e}")
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

async def api_get_users(search: str = None, monitoring: int = None):
    try:
        async with get_db_session() as session:
            stmt = select(
                User.id,
                User.name,
                User.surname,
                User.phone,
                User.link,
                User.status_id
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