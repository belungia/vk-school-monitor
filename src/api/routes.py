from fastapi import FastAPI, Query
from fastapi.responses import FileResponse

from src.api.dto.base import BaseResponse
from src.db.methods.user import api_get_users, api_update_user_status
from src.api.dto.schemas import MonitoringUpdateRequest


app = FastAPI()


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
async def get_alerts():
    ...

@app.post("/api/users")
async def add_user():
    ...

@app.post("/api/users/import")
async def add_users_from_file():
    ...


