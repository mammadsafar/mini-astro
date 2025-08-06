from pydantic import BaseModel, Field
from typing import Optional, Any, Generic, TypeVar
from datetime import datetime

T = TypeVar('T')

class StandardResponse(BaseModel, Generic[T]):
    success: bool = Field(..., description="وضعیت موفقیت عملیات")
    data: Optional[T] = Field(None, description="داده‌های پاسخ")
    message: str = Field(..., description="پیام پاسخ")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ErrorResponse(BaseModel):
    success: bool = False
    error: str = Field(..., description="نوع خطا")
    message: str = Field(..., description="پیام خطا")
    details: Optional[dict] = Field(None, description="جزئیات خطا")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class PaginationInfo(BaseModel):
    page: int = Field(..., description="شماره صفحه")
    per_page: int = Field(..., description="تعداد آیتم در هر صفحه")
    total: int = Field(..., description="کل تعداد آیتم‌ها")
    total_pages: int = Field(..., description="کل تعداد صفحات")
    has_next: bool = Field(..., description="آیا صفحه بعدی وجود دارد")
    has_prev: bool = Field(..., description="آیا صفحه قبلی وجود دارد")

class PaginatedResponse(BaseModel, Generic[T]):
    success: bool = True
    data: list[T] = Field(..., description="لیست داده‌ها")
    pagination: PaginationInfo = Field(..., description="اطلاعات صفحه‌بندی")
    message: str = Field("عملیات با موفقیت انجام شد", description="پیام پاسخ")
    timestamp: datetime = Field(default_factory=datetime.utcnow)