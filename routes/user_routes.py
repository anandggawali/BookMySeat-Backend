from fastapi import APIRouter, Depends

from dependencies.auth_dependency import get_current_user
from schemas.fcm_schema import FCMTokenRequest
from services.user_service import UserService

router = APIRouter(
    prefix="/api/users",
    tags=["Users"]
)


@router.get("/profile")
def profile(
        current_user=Depends(get_current_user)
):
    return current_user

@router.post("/fcm-token")
def save_fcm_token(
        request: FCMTokenRequest,
        current_user=Depends(get_current_user)
):
    print("========== ROUTE ==========")
    print(current_user)
    print(request.token)

    return UserService.save_fcm_token(
        current_user["userId"],
        request.token
    )