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

        token = create_access_token({
            "userId": user["userId"],
            "role": user["role"]
        })

        return {
            "token": token,
            "userId": user["userId"],
            "role": user["role"]
        }