from fastapi import APIRouter, Depends

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