from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas.user import UserCreate, UserOut, UserUpdate, UserLogin
from schemas.response import StandardResponse, PaginatedResponse
from services import user_service
from core.dependencies import get_db
from core.security import get_current_user, get_current_user_with_role, require_role
from typing import List, Optional
import uuid

router = APIRouter()

# Admin endpoints - require admin role
@router.post("/admin/create", response_model=StandardResponse[UserOut])
async def admin_create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    admin_data: dict = Depends(require_role("admin"))
):
    """ایجاد کاربر جدید توسط ادمین"""
    # Check if user already exists
    existing_user = user_service.get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="این ایمیل قبلاً ثبت شده است")
    
    db_user = user_service.create_user(db, user)
    return StandardResponse(
        success=True,
        data=db_user,
        message="کاربر با موفقیت ایجاد شد"
    )

@router.get("/admin/", response_model=PaginatedResponse[UserOut])
async def admin_list_users(
    page: int = 1,
    per_page: int = 20,
    db: Session = Depends(get_db),
    admin_data: dict = Depends(require_role("admin"))
):
    """لیست تمام کاربران (فقط ادمین)"""
    skip = (page - 1) * per_page
    users = user_service.get_all_users_paginated(db, skip, per_page)
    total = user_service.get_users_count(db)
    
    from schemas.response import PaginationInfo
    pagination = PaginationInfo(
        page=page,
        per_page=per_page,
        total=total,
        total_pages=(total + per_page - 1) // per_page,
        has_next=page * per_page < total,
        has_prev=page > 1
    )
    
    return PaginatedResponse(
        data=users,
        pagination=pagination,
        message="لیست کاربران با موفقیت دریافت شد"
    )

@router.get("/admin/{user_id}", response_model=StandardResponse[UserOut])
async def admin_get_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    admin_data: dict = Depends(require_role("admin"))
):
    """دریافت اطلاعات کاربر (فقط ادمین)"""
    user = user_service.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="کاربر یافت نشد")
    
    return StandardResponse(
        success=True,
        data=user,
        message="اطلاعات کاربر با موفقیت دریافت شد"
    )

@router.put("/admin/{user_id}", response_model=StandardResponse[UserOut])
async def admin_update_user(
    user_id: uuid.UUID,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    admin_data: dict = Depends(require_role("admin"))
):
    """به‌روزرسانی اطلاعات کاربر (فقط ادمین)"""
    user = user_service.update_user(db, user_id, user_update)
    if not user:
        raise HTTPException(status_code=404, detail="کاربر یافت نشد")
    
    return StandardResponse(
        success=True,
        data=user,
        message="اطلاعات کاربر با موفقیت به‌روزرسانی شد"
    )

@router.delete("/admin/{user_id}", response_model=StandardResponse[dict])
async def admin_delete_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    admin_data: dict = Depends(require_role("admin"))
):
    """حذف کاربر (فقط ادمین)"""
    success = user_service.delete_user(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="کاربر یافت نشد")
    
    return StandardResponse(
        success=True,
        data={"deleted": True},
        message="کاربر با موفقیت حذف شد"
    )

# Regular user endpoints - require authentication
@router.get("/me", response_model=StandardResponse[UserOut])
async def get_current_user_info(
    db: Session = Depends(get_db),
    current_user: uuid.UUID = Depends(get_current_user)
):
    """دریافت اطلاعات کاربر فعلی"""
    user = user_service.get_user(db, current_user)
    if not user:
        raise HTTPException(status_code=404, detail="کاربر یافت نشد")
    
    return StandardResponse(
        success=True,
        data=user,
        message="اطلاعات کاربر با موفقیت دریافت شد"
    )

@router.put("/me", response_model=StandardResponse[UserOut])
async def update_current_user(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: uuid.UUID = Depends(get_current_user)
):
    """به‌روزرسانی اطلاعات کاربر فعلی"""
    user = user_service.update_user(db, current_user, user_update)
    if not user:
        raise HTTPException(status_code=404, detail="کاربر یافت نشد")
    
    return StandardResponse(
        success=True,
        data=user,
        message="اطلاعات کاربر با موفقیت به‌روزرسانی شد"
    )