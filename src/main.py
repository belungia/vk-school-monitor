import asyncio
import uvicorn

from src.db.methods.group import add_groups, add_user_groups, get_monitored_groups_last_post_dates, update_group_last_post_dates
from src.db.methods.post import add_posts
from src.client import VKCLient
from src.client.scripts import wall_get_script
from src.db.methods.user import api_get_users, api_add_users, api_add_users, get_tracked_users_last_post_dates, update_last_post_dates
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
    # print(users_last_post_dates_map)
    # async with VKCLient() as vk:
    #     posts = await vk.wall_get(users_last_post_dates_map)
    # await add_posts(posts)

    # await analyze_posts()

    await uvicorn.run("src.main:app", reload=True)

    # async with VKCLient() as vk:
    #     users = await vk.users_get(["https://vk.com/keeeshik", "https://vk.com/rosteuro", "https://vk.com/id516793241"])
    # await api_add_users(users)
    
    # await update_last_post_dates()

    # async with VKCLient() as vk:
    #     groups = await vk.groups_get([278844800, 418648413])
    # print(groups)

    # -----------------------------
    # 1. Получаем группы пользователей
    # -----------------------------
    # test_user_ids = [278844800, 418648413]  # замени на реальные ID
    # async with VKCLient() as vk:
    #     groups = await vk.groups_get(test_user_ids)
    # print(f"Найдено групп: {len(groups)}")

    # # -----------------------------
    # # 2. Сохраняем группы в БД
    # # -----------------------------
    # if groups:
    #     added_groups = await add_groups(groups)  # из src.db.methods.group
    #     print(f"Добавлено новых групп: {added_groups}")

    # # -----------------------------
    # # 3. Сохраняем связи пользователь-группа
    # # -----------------------------
    # subscriptions = []
    # for user_id in test_user_ids:
    #     for g in groups:
    #         subscriptions.append({"user_id": user_id, "group_id": g["id"]})
    # if subscriptions:
    #     added_links = await add_user_groups(subscriptions)  # из src.db.methods.group
    #     print(f"Добавлено связей пользователь-группа: {added_links}")

    # # -----------------------------
    # # 4. Получаем last_post_date для мониторируемых групп
    # # -----------------------------
    # group_last_dates = await get_monitored_groups_last_post_dates()  # из src.db.methods.group
    # print(f"Групп на мониторинге (status_id=1): {len(group_last_dates)}")
    # print("last_post_date для групп:", group_last_dates)

    # # -----------------------------
    # # 5. Собираем посты с помощью универсального wall_get
    # # -----------------------------
    # # Преобразуем ключи в отрицательные owner_id
    # group_owner_map = {-gid: last_date for gid, last_date in group_last_dates.items()}

    # if group_owner_map:
    #     async with VKCLient() as vk:
    #         new_posts = await vk.wall_get(group_owner_map)
    #     print(f"Получено постов от групп: {len(new_posts)}")
    #     if new_posts:

    #         # -----------------------------
    #         # 6. Сохраняем посты
    #         # -----------------------------
    #         added_posts = await add_posts(new_posts)  # из src.db.methods.post
    #         print(f"Сохранено новых постов: {added_posts}")

    #         # -----------------------------
    #         # 7. Обновляем last_post_date у групп
    #         # -----------------------------
    #         await update_group_last_post_dates()  # из src.db.methods.group
    #         print("Даты последних постов групп обновлены")

    # group_ids = [148506755, 189049481, 140774741, 178708867, 143975801, 90606522, 175282147, 10537686, 185750389]

    # from src.client.scripts import wall_get_script
    # script = wall_get_script(group_ids)

    # async with VKCLient() as vk:
    #     full_response = await vk._execute_raw(script)
    #     import json
    #     print(json.dumps(full_response, indent=2, ensure_ascii=False))
    # return



if __name__ == "__main__":
    asyncio.run(main())