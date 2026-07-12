import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field
class AuthBase(BaseModel):
    model_config = {"from_attributes": True}

class RegisterRequest(AuthBase):
    phone: str = Field(min_length=10, max_length=15)
    email: EmailStr | None = None
    full_name: str = Field(min_length=1, max_length=100)
 

 
class RegisterResponse(AuthBase):
    message: str
    user: object
 
    
class LoginRequest(AuthBase):
    phone: str
    otp: str = Field(min_length=6, max_length=6)

class LoginResponse(AuthBase):
    access_token: str
    message: str
    # tokens set as HttpOnly cookies by router, never in response body
    
class LogoutResponse(AuthBase):
    message: str
 

class VerificationCodeRequest(AuthBase):
    phone: str

class VerificationCodeResponse(AuthBase):
    otp: str

class VerifyVerificationCodeRequest(AuthBase):
    phone: str
    otp: str
    
class UserResponse(AuthBase):
    id: uuid.UUID
    phone: str
    email: str | None
    full_name: str
    role: str
    created_at: datetime
    last_login_at: datetime | None
 