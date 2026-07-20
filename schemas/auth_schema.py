from pydantic import BaseModel ,EmailStr


class RegisterRequest(BaseModel):
    name: str
    phoneNo: str
    password: str
    email: EmailStr


class LoginRequest(BaseModel):
    phoneNo: str
    password: str



class LoginResponse(BaseModel):
    token: str
    userId: str
    role: str
    name: str
    phoneNo: str
    email: str


class UpdateProfileRequest(BaseModel):
    name: str
    # phoneNo: str
    email: EmailStr