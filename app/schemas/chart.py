from pydantic import BaseModel, Field
from datetime import date, time, datetime
from typing import Optional, Dict, Any, List
from uuid import UUID

class ChartBase(BaseModel):
    label: str = Field(..., description="نام چارت مثل 'من'، 'مامان'")
    category: Optional[str] = Field(None, description="دسته‌بندی: self, friend, partner, client")
    chart_type: str = Field(..., description="نوع چارت: natal, composite, transit, synastry")
    visibility: str = Field("private", description="قابلیت مشاهده: private, public")
    
    # Birth data
    birth_date: date = Field(..., description="تاریخ تولد")
    birth_time: time = Field(..., description="ساعت تولد")
    lat: float = Field(..., description="عرض جغرافیایی")
    lng: float = Field(..., description="طول جغرافیایی")
    city: str = Field(..., description="شهر تولد")
    timezone: str = Field(..., description="منطقه زمانی مثل Asia/Tehran")
    timezone_offset: Optional[str] = Field(None, description="اختلاف زمانی مثل +03:30")
    
    # Additional fields
    description: Optional[str] = Field(None, description="توضیحات چارت")
    notes: Optional[str] = Field(None, description="یادداشت‌های شخصی")
    tags: Optional[List[str]] = Field(None, description="برچسب‌ها")

class ChartCreate(ChartBase):
    pass

class ChartUpdate(BaseModel):
    label: Optional[str] = None
    category: Optional[str] = None
    chart_type: Optional[str] = None
    visibility: Optional[str] = None
    birth_date: Optional[date] = None
    birth_time: Optional[time] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    city: Optional[str] = None
    timezone: Optional[str] = None
    timezone_offset: Optional[str] = None
    description: Optional[str] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None

class ChartOut(ChartBase):
    id: UUID
    user_id: UUID
    chart_json: Optional[Dict[str, Any]] = None
    chart_svg_url: Optional[str] = None
    source_api: Optional[str] = None
    is_deleted: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ChartList(BaseModel):
    charts: List[ChartOut]
    total: int
    page: int
    per_page: int

class BulkDeleteRequest(BaseModel):
    chart_ids: List[UUID] = Field(..., description="لیست ID چارت‌هایی که باید حذف شوند")

class AstroInput(BaseModel):
    name: str = Field(..., example="Alice")
    year: int = Field(..., example=1990)
    month: int = Field(..., example=5)
    day: int = Field(..., example=15)
    hour: int = Field(..., example=14)
    minute: int = Field(..., example=30)
    lat: float = Field(..., example=35.6892)
    lng: float = Field(..., example=51.3890)
    city: str = Field(..., example="Tehran")
    tz_str: str = Field(..., example="Asia/Tehran")

class AstroPairInput(BaseModel):
    person1: AstroInput
    person2: AstroInput 