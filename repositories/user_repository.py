from core.database import users_collection


class UserRepository:

    @staticmethod
    def find_by_phone(phone_no: str):
        return users_collection.find_one(
            {"phoneNo": phone_no}
        )

    @staticmethod
    def save(user: dict):
        return users_collection.insert_one(user)

    @staticmethod
    def find_by_id(user_id: str):
        return users_collection.find_one(
            {"userId": user_id}
        )

    @staticmethod
    def save_fcm_token(
            user_id,
            token
    ):
        print("========== SAVE FCM ==========")
        print("User ID :", user_id)
        print("Token :", token)

        result = users_collection.update_one(
            {
                "userId": user_id
            },
            {
                "$set": {
                    "fcmToken": token
                }
            }
        )

        print("Matched :", result.matched_count)
        print("Modified:", result.modified_count)
        