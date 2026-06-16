from pydantic import BaseModel, Field


class MonitoringUpdateRequest(BaseModel):
    status_id: int = Field(..., ge=0, le=1, description="0 - off, 1 - on")


class AddUserRequest(BaseModel):
    link: str
    phone: str | None = None


class AddGroupRequest(BaseModel):
    link: str