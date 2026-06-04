import bcrypt
from datetime import datetime, timedelta
from jose import jwt

SECRET_KEY = "bookmyseat_secret_key"
ALGORITHM = "HS256"


def hash_password(password: str):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(
        password.encode("utf-8"),
        salt
    ).decode("utf-8")


def verify_password(
        plain_password: str,
        hashed_password: str
):
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )


def create_access_token(data: dict):

    payload = data.copy()

    payload["exp"] = (
        datetime.utcnow()
        + timedelta(days=1)
    )

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


def verify_token(token: str):

    try:
        return jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

    except Exception:
        return None