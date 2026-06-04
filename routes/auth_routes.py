from fastapi import APIRouter

from schemas.auth_schema import RegisterRequest
from schemas.auth_schema import LoginRequest

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