from firebase_admin import messaging


class NotificationService:

    @staticmethod
    def send_notification(
        token,
        title,
        body,
        notification_id,
        type,
        click_action,
        color
    ):

        message = messaging.Message(

            notification=messaging.Notification(
                title=title,
                body=body
            ),

            data={
                "notificationId": notification_id,
                "type": type,
                "click_action": click_action,
                "color": color
            },

            token=token
        )

        response = messaging.send(message)

        print("Firebase Response:", response)

        return response