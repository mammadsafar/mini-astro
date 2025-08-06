from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from core.dependencies import get_db
from core.security import get_current_user, require_role
from schemas.chart import ChartCreate, ChartUpdate, ChartOut, ChartList, BulkDeleteRequest
from schemas.response import StandardResponse, PaginatedResponse, ErrorResponse
from services.chart_service import (
    create_chart, get_user_charts, get_chart_by_id, 
    update_chart, delete_chart, bulk_delete_charts,
    get_chart_count, search_charts, get_all_charts, get_all_charts_count
)
import uuid

router = APIRouter()

@router.post("/", response_model=StandardResponse[ChartOut])
async def create_new_chart(
    chart: ChartCreate,
    db: Session = Depends(get_db),
    current_user: uuid.UUID = Depends(get_current_user)
):
    """ایجاد چارت جدید"""
    try:
        db_chart = create_chart(db, current_user, chart)
        return StandardResponse(
            success=True,
            data=db_chart,
            message="چارت با موفقیت ایجاد شد"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=PaginatedResponse[ChartOut])
async def list_user_charts(
    page: int = Query(1, ge=1, description="شماره صفحه"),
    per_page: int = Query(20, ge=1, le=100, description="تعداد آیتم در هر صفحه"),
    category: Optional[str] = Query(None, description="فیلتر بر اساس دسته‌بندی"),
    chart_type: Optional[str] = Query(None, description="فیلتر بر اساس نوع چارت"),
    db: Session = Depends(get_db),
    current_user: uuid.UUID = Depends(get_current_user)
):
    """دریافت لیست چارت‌های کاربر"""
    skip = (page - 1) * per_page
    charts = get_user_charts(db, current_user, skip, per_page, category, chart_type)
    total = get_chart_count(db, current_user)
    
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
        data=charts,
        pagination=pagination,
        message="لیست چارت‌ها با موفقیت دریافت شد"
    )

@router.get("/{chart_id}", response_model=StandardResponse[ChartOut])
async def get_chart(
    chart_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: uuid.UUID = Depends(get_current_user)
):
    """دریافت چارت خاص"""
    chart = get_chart_by_id(db, chart_id, current_user)
    if not chart:
        raise HTTPException(status_code=404, detail="چارت یافت نشد")
    
    return StandardResponse(
        success=True,
        data=chart,
        message="چارت با موفقیت دریافت شد"
    )

@router.put("/{chart_id}", response_model=StandardResponse[ChartOut])
async def update_chart_data(
    chart_id: uuid.UUID,
    chart_update: ChartUpdate,
    db: Session = Depends(get_db),
    current_user: uuid.UUID = Depends(get_current_user)
):
    """به‌روزرسانی چارت"""
    chart = update_chart(db, chart_id, current_user, chart_update)
    if not chart:
        raise HTTPException(status_code=404, detail="چارت یافت نشد یا دسترسی ندارید")
    
    return StandardResponse(
        success=True,
        data=chart,
        message="چارت با موفقیت به‌روزرسانی شد"
    )

@router.delete("/{chart_id}", response_model=StandardResponse[dict])
async def delete_chart_data(
    chart_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: uuid.UUID = Depends(get_current_user)
):
    """حذف چارت"""
    success = delete_chart(db, chart_id, current_user)
    if not success:
        raise HTTPException(status_code=404, detail="چارت یافت نشد یا دسترسی ندارید")
    
    return StandardResponse(
        success=True,
        data={"deleted": True},
        message="چارت با موفقیت حذف شد"
    )

@router.post("/delete-multiple", response_model=StandardResponse[dict])
async def bulk_delete_charts_data(
    request: BulkDeleteRequest,
    db: Session = Depends(get_db),
    current_user: uuid.UUID = Depends(get_current_user)
):
    """حذف چندین چارت به صورت همزمان"""
    deleted_count = bulk_delete_charts(db, request.chart_ids, current_user)
    
    return StandardResponse(
        success=True,
        data={"deleted_count": deleted_count},
        message=f"{deleted_count} چارت با موفقیت حذف شد"
    )

@router.get("/search/", response_model=PaginatedResponse[ChartOut])
async def search_user_charts(
    q: str = Query(..., description="عبارت جستجو"),
    page: int = Query(1, ge=1, description="شماره صفحه"),
    per_page: int = Query(20, ge=1, le=100, description="تعداد آیتم در هر صفحه"),
    db: Session = Depends(get_db),
    current_user: uuid.UUID = Depends(get_current_user)
):
    """جستجو در چارت‌های کاربر"""
    skip = (page - 1) * per_page
    charts = search_charts(db, current_user, q, skip, per_page)
    
    from schemas.response import PaginationInfo
    pagination = PaginationInfo(
        page=page,
        per_page=per_page,
        total=len(charts),  # This should be optimized
        total_pages=(len(charts) + per_page - 1) // per_page,
        has_next=page * per_page < len(charts),
        has_prev=page > 1
    )
    
    return PaginatedResponse(
        data=charts,
        pagination=pagination,
        message="نتایج جستجو با موفقیت دریافت شد"
    )

# Admin endpoints - require admin role
@router.get("/admin/", response_model=PaginatedResponse[ChartOut])
async def admin_list_all_charts(
    page: int = Query(1, ge=1, description="شماره صفحه"),
    per_page: int = Query(20, ge=1, le=100, description="تعداد آیتم در هر صفحه"),
    db: Session = Depends(get_db),
    admin_data: dict = Depends(require_role("admin"))
):
    """لیست تمام چارت‌ها (فقط ادمین)"""
    skip = (page - 1) * per_page
    charts = get_all_charts(db, skip, per_page)
    total = get_all_charts_count(db)
    
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
        data=charts,
        pagination=pagination,
        message="لیست تمام چارت‌ها با موفقیت دریافت شد"
    )

@router.get("/admin/{chart_id}", response_model=StandardResponse[ChartOut])
async def admin_get_chart(
    chart_id: uuid.UUID,
    db: Session = Depends(get_db),
    admin_data: dict = Depends(require_role("admin"))
):
    """دریافت چارت خاص (فقط ادمین)"""
    chart = get_chart_by_id(db, chart_id, None)  # Admin can access any chart
    if not chart:
        raise HTTPException(status_code=404, detail="چارت یافت نشد")
    
    return StandardResponse(
        success=True,
        data=chart,
        message="چارت با موفقیت دریافت شد"
    )

@router.put("/admin/{chart_id}", response_model=StandardResponse[ChartOut])
async def admin_update_chart(
    chart_id: uuid.UUID,
    chart_update: ChartUpdate,
    db: Session = Depends(get_db),
    admin_data: dict = Depends(require_role("admin"))
):
    """به‌روزرسانی چارت (فقط ادمین)"""
    chart = update_chart(db, chart_id, None, chart_update)  # Admin can update any chart
    if not chart:
        raise HTTPException(status_code=404, detail="چارت یافت نشد")
    
    return StandardResponse(
        success=True,
        data=chart,
        message="چارت با موفقیت به‌روزرسانی شد"
    )

@router.delete("/admin/{chart_id}", response_model=StandardResponse[dict])
async def admin_delete_chart(
    chart_id: uuid.UUID,
    db: Session = Depends(get_db),
    admin_data: dict = Depends(require_role("admin"))
):
    """حذف چارت (فقط ادمین)"""
    success = delete_chart(db, chart_id, None)  # Admin can delete any chart
    if not success:
        raise HTTPException(status_code=404, detail="چارت یافت نشد")
    
    return StandardResponse(
        success=True,
        data={"deleted": True},
        message="چارت با موفقیت حذف شد"
    ) 