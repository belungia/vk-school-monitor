import asyncio
import logging
from fastapi import FastAPI, File, Query, UploadFile
from fastapi.responses import FileResponse

from src.collector import collect_and_analyze_users_posts
from src.db.methods.group import api_get_groups, api_update_group_status
from src.client.vk_client import VKCLient
from src.api.dto.base import BaseResponse
from src.db.methods.user import api_add_users, api_get_users, api_update_user_status
from src.db.methods.alert import api_get_alerts
from src.api.dto.schemas import AddUserRequest, MonitoringUpdateRequest
from src.utils.utils import extract_links_from_file_text


app = FastAPI()
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def start_background_tasks():
    async def daily_collector():
        while True:
            try:
                result = await collect_and_analyze_users_posts()
                logger.info(f"Ежедневный сбор завершён: {result}")
            except Exception as e:
                logger.error(f"Ошибка ежедневного сбора: {e}")
            await asyncio.sleep(86400)

    asyncio.create_task(daily_collector())

@app.get("/")
async def root():
    return FileResponse("web/index.html")

@app.get("/api/users")
async def get_users(search: str = Query(None), monitoring: int = Query(None)):
    try:
        users = await api_get_users(search=search, monitoring=monitoring)
        return users
    
    except Exception as e:
        return BaseResponse(error=True, message="Internal server error")
    
@app.patch("/api/users/{user_id}/monitoring")
async def update_user_status(user_id: int, data: MonitoringUpdateRequest):
    try:
        result = await api_update_user_status(user_id, data.status_id)
        return result
    
    except Exception as e:
        return BaseResponse(error=True, message="Internal server error")

@app.get("/api/alerts")
async def get_alerts(search: str = Query(None)):
    try:
        return await api_get_alerts(search=search)
    
    except Exception as e:
        return BaseResponse(error=True, message="Internal server error")

@app.post("/api/users")
async def add_user(req: AddUserRequest):
    try:
        async with VKCLient() as client:
            users = await client.users_get([req.link])
        if not users:
            return BaseResponse(error=True, message="Пользователь не найден в ВК")
        user = users[0]
        user["phone"] = req.phone

        added = await api_add_users([user])
        if added:
            return BaseResponse(error=False, message="Пользователь добавлен", data=user)
        else:
            return BaseResponse(error=False, message="Пользователь уже существует в базе")
        
    except Exception as e:
        return BaseResponse(error=True, message="Internal server error")


@app.post("/api/users/import")
async def add_users_from_file(file: UploadFile = File(...)):
    try:
        content = await file.read()
        text = content.decode("utf-8")
        links = extract_links_from_file_text(text)
        if not links:
            return BaseResponse(error=True, message="Не найдено ни одной ссылки vk.com в файле")

        async with VKCLient() as client:
            users = await client.users_get(links)

        if not users:
            return BaseResponse(error=True, message="Не удалось получить данные ни по одной ссылке")

        added_count = await api_add_users(users)
        return BaseResponse(
            error=False,
            message=f"Добавлено {added_count} новых пользователей из {len(links)} ссылок",
            payload={"added": added_count, "total": len(links)}
        )
    except Exception as e:
        return BaseResponse(error=True, message="Internal server error")
    
@app.get("/api/groups")
async def get_groups(search: str = None, monitoring: int = None):
    try:
        groups = await api_get_groups(search=search, monitoring=monitoring)
        return groups
    except Exception as e:
        return BaseResponse(error=True, message="Internal server error")

@app.patch("/api/groups/{group_id}/monitoring")
async def update_group_monitoring(group_id: int, data: MonitoringUpdateRequest):
    try:
        result = await api_update_group_status(group_id, data.status_id)
        return result
    except Exception as e:
        return BaseResponse(error=True, message="Internal server error")

@app.post("api/users/check")
async def force_check_users():
    try:
        result = await collect_and_analyze_users_posts()
        return BaseResponse(
            error=False,
            message=f"Собрано {result['new_posts']} новых постов, создано {result['alerts']} уведомлений",
            data=result
        )
    except Exception as e:
        return BaseResponse(error=True, message="Внутренняя ошибка сервера")

