from pydantic import BaseModel, EmailStr
from datetime import date, datetime
from typing import Optional
from uuid import UUID

class UserBase(BaseModel):
    email: EmailStr
    full_name: str

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_premium: Optional[bool] = None
    role: Optional[str] = None

class UserOut(UserBase):
    id: UUID
    is_premium: bool
    role: str
    created_at: datetime

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str