import logging
from src.client.vk_client import VKCLient
from src.db.methods.user import get_tracked_users_last_post_dates, update_last_post_dates
from src.db.methods.post import add_posts, get_unanalyzed_posts, update_statuses
from src.db.methods.alert import add_alerts

logger = logging.getLogger(__name__)

async def collect_and_analyze_users_posts():
    last_dates = await get_tracked_users_last_post_dates()
    if not last_dates:
        return {"new_posts": 0, "alerts": 0}

    async with VKCLient() as vk:
        new_posts = await vk.wall_get(last_dates)

    if not new_posts:
        return {"new_posts": 0, "alerts": 0}

    added = await add_posts(new_posts)

    await update_last_post_dates()

    unanalyzed = await get_unanalyzed_posts()
    alerts_list = []
    for post_id, user_id, group_id, text in unanalyzed:
        if group_id is not None:
            continue
        if user_id is None:
            continue
        alerts_list.append({
            "user_id": user_id,
            "post_id": post_id,
            "reason": "Обнаружен потенциально деструктивный контент (тестовый алерт)"
        })
    
    if alerts_list:
        await add_alerts(alerts_list)
    
    processed_ids = [p[0] for p in unanalyzed]
    await update_statuses(processed_ids)

    return {"new_posts": added, "alerts": len(alerts_list)}