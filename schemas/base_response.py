from typing import Any, Optional
from pydantic import BaseModel


class BaseResponse(BaseModel):
    status: int
    message: str
    errorMessage: Optional[str] = ""
    data: Optional[Any] = None