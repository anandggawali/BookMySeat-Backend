from fastapi import APIRouter, Depends
from schemas.forgot_password_schema import (
    SendOtpRequest,
    VerifyOtpRequest,
    ResetPasswordRequest
)
from schemas.auth_schema import RegisterOtpRequest
from schemas.auth_schema import RegisterVerifyRequest
from schemas.auth_schema import RegisterRequest
from schemas.auth_schema import LoginRequest
from schemas.auth_schema import ChangePasswordRequest
from dependencies.auth_dependency import get_current_user
from services.auth_service import AuthService

router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"]
)


@router.post("/register")
def register(request: RegisterRequest):
    return AuthService.register(request)


@router.post("/login")
def login(request: LoginRequest):
    return AuthService.login(request)

@router.put("/change-password")
def change_password(

        request: ChangePasswordRequest,

        current_user=Depends(get_current_user)


):

    return AuthService.change_password(
        current_user,
        request
    )

@router.post("/send-otp")
def send_otp(request: SendOtpRequest):

    return AuthService.send_otp(request)


@router.post("/verify-otp")
def verify_otp(request: VerifyOtpRequest):

    return AuthService.verify_otp(request)


@router.put("/reset-password")
def reset_password(request: ResetPasswordRequest):

    return AuthService.reset_password(request)

@router.post("/register/send-otp")
def register_send_otp(request: RegisterOtpRequest):
    return AuthService.register_send_otp(request)


@router.post("/register/verify")
def register_verify(request: RegisterVerifyRequest):
    return AuthService.register_verify(request)