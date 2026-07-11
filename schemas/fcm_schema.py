from pydantic import BaseModel


class FCMTokenRequest(BaseModel):
    token: str