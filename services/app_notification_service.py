import uuid
from datetime import datetime

from repositories.notification_repository import NotificationRepository
from repositories.user_repository import UserRepository
from services.notification_service import NotificationService


class AppNotificationService:

    @staticmethod
    def create_notification(
            user_id,
            title,
            body,
            type,
            click_action,
            color
    ):
        print("========== APP NOTIFICATION ==========")
        print(user_id)
        print(title)
        user = UserRepository.find_by_id(user_id)

        notification = {

            "notificationId": str(uuid.uuid4()),

            "userId": user_id,

            "title": title,

            "body": body,

            "type": type,

            "click_action": click_action,

            "color": color,

            "isRead": False,

            "createdAt": datetime.utcnow().isoformat()

        }
        print("Saving notification...")
        # Save notification into MongoDB
        NotificationRepository.save(notification)
        print("Notification saved.")
        # Send FCM Push Notification
        if user and user.get("fcmToken"):
            print("User:", user)

            print("FCM:", user.get("fcmToken"))
            NotificationService.send_notification(

                token=user["fcmToken"],

                title=title,

                body=body,

                notification_id=notification["notificationId"],

                type=type,

                click_action=click_action,

                color=color

            )


        return notification