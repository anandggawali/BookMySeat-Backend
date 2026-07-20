from fastapi import APIRouter, Depends

from dependencies.auth_dependency import get_current_user
from repositories.user_repository import UserRepository
from schemas.auth_schema import UpdateProfileRequest
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
    return UserRepository.get_profile(
        current_user["userId"]
    )

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

@router.put("/profile")
def update_profile(

        request: UpdateProfileRequest,

        current_user=Depends(get_current_user)

):

    UserRepository.update_profile(

        current_user["userId"],
        request

    )

    return {

        "message": "Profile updated successfully"

    }

@router.delete("/profile")
def delete_profile(

        current_user=Depends(get_current_user)

):

    UserRepository.delete_user(

        current_user["userId"]

    )

    return {

        "message": "Account deleted"

    }