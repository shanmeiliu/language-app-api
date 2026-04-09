from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class RegisterLocalUserRequest(BaseModel):
    password: str = Field(..., min_length=8)
    email: Optional[EmailStr] = None


class LoginPasswordRequest(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    user_id: str
    account_type: str
    email: Optional[str] = None
    username: str
    is_active: bool