import uuid
import random

from services.email_service import EmailService
from repositories.user_repository import UserRepository
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

    @staticmethod
    def send_otp(request):

        user = UserRepository.find_by_email(
            request.email
        )

        if not user:
            return {
                "message": "Email not registered"
            }

        otp = str(random.randint(100000, 999999))

        UserRepository.save_otp(
            request.email,
            otp
        )

        EmailService.send_otp(
            request.email,
            otp
        )

        return {
            "message": "OTP sent successfully"
        }

    @staticmethod
    def verify_otp(request):

        user = UserRepository.verify_otp(
            request.email,
            request.otp
        )

        if not user:
            raise HTTPException(
                status_code=400,
                detail="Invalid OTP"
            )

        from core.database import users_collection

        users_collection.update_one(

            {
                "email": request.email
            },

            {
                "$set": {
                    "otpVerified": True
                }
            }

        )

        return {
            "message": "OTP verified"
        }

    @staticmethod
    def reset_password(request):

        user = UserRepository.find_by_email(
            request.email
        )

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        if not user.get("otpVerified", False):
            raise HTTPException(
                status_code=400,
                detail="OTP not verified"
            )

        UserRepository.update_password(

            user["userId"],

            hash_password(request.password)

        )

        return {
            "message": "Password changed successfully"
        }

    @staticmethod
    def register_send_otp(request):

        if UserRepository.find_by_phone(request.phoneNo):
            return {
                "message": "Phone number already registered"
            }

        if UserRepository.find_by_email(request.email):
            return {
                "message": "Email already registered"
            }

        otp = str(random.randint(100000, 999999))

        UserRepository.save_otp(
            request.email,
            otp
        )

        EmailService.send_otp(
            request.email,
            otp
        )

        return {
            "message": "OTP sent successfully"
        }

    @staticmethod
    def register_verify(request):

        user = UserRepository.verify_otp(
            request.email,
            request.otp
        )

        if not user:
            return {
                "message": "Invalid OTP"
            }

        newUser = {

            "userId": str(uuid.uuid4()),
            "name": request.name,
            "phoneNo": request.phoneNo,
            "email": request.email,
            "password": hash_password(request.password),
            "role": "MEMBER"

        }

        UserRepository.save(newUser)

        UserRepository.clear_otp(
            request.email
        )

        return {
            "message": "Registration successful"
        }

    