from typing import Any

from pydantic import BaseModel


class BaseResponse(BaseModel):
    error: bool = False
    message: str = "OK"
    payload: Any | None = None