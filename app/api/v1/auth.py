from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.dependencies import get_db
from core.security import create_access_token, get_password_hash, verify_password, get_current_user
from schemas.auth import Token, LoginRequest, RegisterRequest, PasswordChangeRequest
from schemas.response import StandardResponse
from services.user_service import create_user, get_user_by_email, authenticate_user, get_user
from datetime import timedelta
from core.config import settings
import uuid

router = APIRouter()

@router.post("/register", response_model=StandardResponse[Token])
async def register_user(
    user_data: RegisterRequest,
    db: Session = Depends(get_db)
):
    """ثبت‌نام کاربر جدید"""
    # Check if user already exists
    existing_user = get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="این ایمیل قبلاً ثبت شده است")
    
    # Create user
    db_user = create_user(db, user_data)
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(db_user.id), "email": db_user.email, "role": db_user.role},
        expires_delta=access_token_expires
    )
    
    return StandardResponse(
        success=True,
        data=Token(
            access_token=access_token,
            token_type="bearer",
            expires_at=access_token_expires
        ),
        message="کاربر با موفقیت ثبت‌نام شد"
    )

@router.post("/login", response_model=StandardResponse[Token])
async def login_user(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """ورود کاربر"""
    user = authenticate_user(db, login_data.email, login_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="ایمیل یا رمز عبور اشتباه است")
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "role": user.role},
        expires_delta=access_token_expires
    )
    
    return StandardResponse(
        success=True,
        data=Token(
            access_token=access_token,
            token_type="bearer",
            expires_at=access_token_expires
        ),
        message="ورود با موفقیت انجام شد"
    )

@router.post("/change-password", response_model=StandardResponse[dict])
async def change_password(
    password_data: PasswordChangeRequest,
    db: Session = Depends(get_db),
    current_user: uuid.UUID = Depends(get_current_user)
):
    """تغییر رمز عبور"""
    user = get_user(db, current_user)
    if not user:
        raise HTTPException(status_code=404, detail="کاربر یافت نشد")
    
    # Verify current password
    if not verify_password(password_data.current_password, user.password_hash):
        raise HTTPException(status_code=400, detail="رمز عبور فعلی اشتباه است")
    
    # Update password
    user.password_hash = get_password_hash(password_data.new_password)
    db.commit()
    
    return StandardResponse(
        success=True,
        data={"message": "رمز عبور با موفقیت تغییر یافت"},
        message="رمز عبور با موفقیت تغییر یافت"
    )

@router.post("/logout", response_model=StandardResponse[dict])
async def logout_user():
    """خروج کاربر (در JWT، خروج در سمت کلاینت انجام می‌شود)"""
    return StandardResponse(
        success=True,
        data={"message": "خروج با موفقیت انجام شد"},
        message="خروج با موفقیت انجام شد"
    )