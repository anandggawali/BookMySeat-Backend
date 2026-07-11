from repositories.user_repository import UserRepository


class UserService:

    @staticmethod
    def save_fcm_token(
            user_id,
            token
    ):
        print("========== SERVICE ==========")
        print(user_id)
        print(token)

        UserRepository.save_fcm_token(
            user_id,
            token
        )

        return {
            "message": "FCM Token Saved Successfully"
        }