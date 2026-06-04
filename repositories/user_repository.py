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