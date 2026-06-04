from pydantic import BaseModel


class RegisterRequest(BaseModel):
    name: str
    phoneNo: str
    password: str


class LoginRequest(BaseModel):
    phoneNo: str
    password: str


class LoginResponse(BaseModel):
    token: str
    userId: str
    role: str