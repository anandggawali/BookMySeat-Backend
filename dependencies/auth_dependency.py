from fastapi import Depends
from fastapi import HTTPException
from fastapi.security import HTTPBearer
from fastapi.security import HTTPAuthorizationCredentials

from core.security import verify_token
from repositories.user_repository import UserRepository

security = HTTPBearer()


def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security)
):

    token = credentials.credentials

    payload = verify_token(token)

    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    user = UserRepository.find_by_id(
        payload["userId"]
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )

    if user.get("deviceId") != payload.get("deviceId"):
        raise HTTPException(
            status_code=401,
            detail="Logged in from another device"
        )

    payload = verify_token(token)
    print("Received Token:", token)

    print("JWT Payload:", payload)

    user = UserRepository.find_by_id(payload["userId"])

    print("DB Device:", user.get("deviceId"))
    print("JWT Device:", payload.get("deviceId"))
    return payload
