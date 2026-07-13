# from fastapi import APIRouter
#
# from repositories.user_repository import UserRepository
# from services.notification_service import NotificationService
#
# router = APIRouter()
#
#
# @router.get("/test-notification")
# def test():
#
#     user = UserRepository.find_by_phone("9876543210")
#
#     if not user:
#         return {
#             "message": "User not found"
#         }
#
#     if not user.get("fcmToken"):
#         return {
#             "message": "User has no FCM token"
#         }
#
#     NotificationService.send_notification(
#
#         token=user["fcmToken"],
#
#         title="BookMySeat",
#
#         body="Your notification system is working!",
#
#         notification_id="NT001",
#
#         type="SYSTEM",
#
#         click_action="OPEN_HOME",
#
#         color="#2196F3"
#     )
#
#     return {
#         "message": "Notification Sent"

from fastapi import APIRouter
from repositories.notification_repository import NotificationRepository

router = APIRouter()

@router.get("/test-db")
def test_db():

    NotificationRepository.save({

        "notificationId": "TEST001",

        "userId": "123",

        "title": "Test",

        "body": "Testing Mongo",

        "type": "SYSTEM",

        "click_action": "OPEN_HOME",

        "color": "#2196F3",

        "isRead": False,

        "createdAt": "2026-07-10"

    })

    return {
        "message": "Inserted"
    }