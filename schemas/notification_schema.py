from pydantic import BaseModel
from datetime import datetime


class NotificationCreate(BaseModel):
    userId: str

    title: str
    body: str

    type: str

    click_action: str

    color: str


class NotificationResponse(BaseModel):
    message: str


class NotificationItem(BaseModel):
    notificationId: str

    userId: str

    title: str
    body: str

    type: str

    click_action: str

    color: str

    isRead: bool

    createdAt: datetime