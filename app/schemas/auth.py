from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_at: datetime

class TokenData(BaseModel):
    user_id: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None

class LoginRequest(BaseModel):
    email: str = Field(..., description="ایمیل کاربر")
    password: str = Field(..., description="رمز عبور")

class RegisterRequest(BaseModel):
    email: str = Field(..., description="ایمیل کاربر")
    password: str = Field(..., description="رمز عبور")
    full_name: str = Field(..., description="نام کامل")

class PasswordChangeRequest(BaseModel):
    current_password: str = Field(..., description="رمز عبور فعلی")
    new_password: str = Field(..., description="رمز عبور جدید")

class PasswordResetRequest(BaseModel):
    email: str = Field(..., description="ایمیل کاربر")

class PasswordResetConfirm(BaseModel):
    token: str = Field(..., description="توکن بازنشانی")
    new_password: str = Field(..., description="رمز عبور جدید") 