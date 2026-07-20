from pydantic import BaseModel


class User(BaseModel):
    userId: str
    name: str
    phoneNo: str
    password: str
    role: str
    email: str | None = None