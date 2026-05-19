import asyncio
import uvicorn

from src.db.methods.post import add_posts
from src.client import VKCLient
from src.client.scripts import wall_get_script
from src.db.methods.user import api_get_users, api_add_user, api_add_users, get_tracked_users_last_post_dates
from src.db.methods.post import get_unanalyzed_posts
from src.agent.agent import analyze_posts
from src.api.routes import app


async def main():
    # async with VKCLient() as vk:
    #     all_posts = []
    #     result = await vk._execute(script=wall_get_script([278844800, 418648413]))
    #     for posts in result:
    #         for post in posts:
    #             all_posts.append({
    #                 "date": post["date"],
    #                 "id": post["id"],
    #                 "owner_id": post["owner_id"],
    #                 "text": post["text"]
    #             })
    #     print(all_posts)

    # await add_user(1, "123", "name", "surname", "922")

    # print(await get_id_last_post_date_map())

    # users_last_post_dates_map = await get_tracked_users_last_post_dates()
    # async with VKCLient() as vk:
    #     posts = await vk.wall_get(users_last_post_dates_map)
    # await add_posts(posts)

    # await analyze_posts()

    await uvicorn.run("src.main:app", reload=True)


if __name__ == "__main__":
    asyncio.run(main())