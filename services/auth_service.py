import uuid

from fastapi import HTTPException

from repositories.user_repository import UserRepository
from core.security import hash_password
from core.security import verify_password
from core.security import create_access_token


class AuthService:

    @staticmethod
    def register(request):

        existing_user = UserRepository.find_by_phone(
            request.phoneNo
        )

        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Phone number already registered"
            )

        user = {
            "userId": str(uuid.uuid4()),
            "name": request.name,
            "phoneNo": request.phoneNo,
            "email": request.email,
            "password": hash_password(request.password),
            "role": "MEMBER"
        }

        UserRepository.save(user)

        return {
            "message": "User registered successfully"
        }

    @staticmethod
    def login(request):

        user = UserRepository.find_by_phone(
            request.phoneNo
        )

        if not user:
            raise HTTPException(
                status_code=401,
                detail="Invalid credentials"
            )

        if not verify_password(
                request.password,
                user["password"]
        ):
            raise HTTPException(
                status_code=401,
                detail="Invalid credentials"
            )
        UserRepository.update_device(
            user["userId"],
            request.deviceId
        )

        token = create_access_token({
            "userId": user["userId"],
            "role": user["role"],
            "deviceId": request.deviceId
        })


        return {
            "token": token,
            "userId": user["userId"],
            "role": user["role"],
            "name": user["name"],
            "phoneNo": user["phoneNo"],
            "email": user.get("email", "")
        }

    @staticmethod
    def change_password(current_user, request):

        user = UserRepository.find_by_id(
            current_user["userId"]
        )

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        if not verify_password(
                request.oldPassword,
                user["password"]
        ):
            raise HTTPException(
                status_code=400,
                detail="Old password is incorrect"
            )

        UserRepository.update_password(

            current_user["userId"],

            hash_password(request.newPassword)

        )

        return {
            "message": "Password changed successfully"
        }