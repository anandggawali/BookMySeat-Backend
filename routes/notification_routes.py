from fastapi import APIRouter, Depends

from dependencies.auth_dependency import get_current_user
from repositories.notification_repository import NotificationRepository
from core.utils import serialize_mongo_list

router = APIRouter(
    prefix="/api/notifications",
    tags=["Notifications"]
)


@router.get("")
def get_notifications(current_user=Depends(get_current_user)):
    notifications = NotificationRepository.get_user_notifications(
        current_user["userId"]
    )

    return serialize_mongo_list(notifications)


@router.put("/{notification_id}/read")
def mark_as_read(
        notification_id: str,
        current_user=Depends(get_current_user)
):
    NotificationRepository.mark_as_read(notification_id)

    return {
        "message": "Notification marked as read"
    }


@router.put("/read-all")
def mark_all_read(
        current_user=Depends(get_current_user)
):
    NotificationRepository.mark_all_as_read(
        current_user["userId"]
    )

    return {
        "message": "All notifications marked as read"
    }