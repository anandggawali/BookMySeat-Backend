from fastapi import APIRouter, Depends

from dependencies.auth_dependency import get_current_user

router = APIRouter(
    prefix="/api/users",
    tags=["Users"]
)


@router.get("/profile")
def profile(
        current_user=Depends(get_current_user)
):
    return current_user