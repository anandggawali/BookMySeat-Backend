import uuid
from datetime import datetime

from core.database import notifications_collection


class NotificationRepository:

    @staticmethod
    def save(notification):

        notification["notificationId"] = str(uuid.uuid4())

        notification["isRead"] = False

        notification["createdAt"] = datetime.utcnow()
        print("Mongo Insert")
        notifications_collection.insert_one(notification)
        print("Mongo Success")
        return notification

    @staticmethod
    def get_user_notifications(user_id):

        return list(

            notifications_collection

            .find(
                {
                    "userId": user_id
                }
            )

            .sort(
                "createdAt",
                -1
            )

        )

    @staticmethod
    def mark_as_read(notification_id):

        notifications_collection.update_one(

            {
                "notificationId": notification_id
            },

            {
                "$set": {
                    "isRead": True
                }
            }

        )

    @staticmethod
    def mark_all_as_read(user_id):
        notifications_collection.update_many(

            {
                "userId": user_id,
                "isRead": False
            },

            {
                "$set": {
                    "isRead": True
                }
            }

        )