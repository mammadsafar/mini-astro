from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from models.chart import Chart
from schemas.chart import ChartCreate, ChartUpdate, ChartOut
from services import astro_service
from typing import List, Optional
import uuid
from datetime import datetime

def create_chart(db: Session, user_id: uuid.UUID, chart_data: ChartCreate) -> Chart:
    """Create a new chart for user"""
    # Generate chart data using astrology service
    astro_input = astro_service.AstroInput(
        name=chart_data.label,
        year=chart_data.birth_date.year,
        month=chart_data.birth_date.month,
        day=chart_data.birth_date.day,
        hour=chart_data.birth_time.hour,
        minute=chart_data.birth_time.minute,
        lat=chart_data.lat,
        lng=chart_data.lng,
        city=chart_data.city,
        tz_str=chart_data.timezone
    )
    
    # Generate chart data
    chart_json = astro_service.generate_natal_chart(astro_input)
    
    # Create chart record
    db_chart = Chart(
        user_id=user_id,
        label=chart_data.label,
        category=chart_data.category,
        chart_type=chart_data.chart_type,
        visibility=chart_data.visibility,
        birth_date=chart_data.birth_date,
        birth_time=chart_data.birth_time,
        lat=chart_data.lat,
        lng=chart_data.lng,
        city=chart_data.city,
        timezone=chart_data.timezone,
        timezone_offset=chart_data.timezone_offset,
        chart_json=chart_json,
        description=chart_data.description,
        notes=chart_data.notes,
        tags=chart_data.tags
    )
    
    db.add(db_chart)
    db.commit()
    db.refresh(db_chart)
    return db_chart

def get_user_charts(
    db: Session, 
    user_id: uuid.UUID, 
    skip: int = 0, 
    limit: int = 100,
    category: Optional[str] = None,
    chart_type: Optional[str] = None
) -> List[Chart]:
    """Get all charts for a user with filtering"""
    query = db.query(Chart).filter(
        and_(
            Chart.user_id == user_id,
            Chart.is_deleted == False
        )
    )
    
    if category:
        query = query.filter(Chart.category == category)
    
    if chart_type:
        query = query.filter(Chart.chart_type == chart_type)
    
    return query.offset(skip).limit(limit).all()

def get_chart_by_id(db: Session, chart_id: uuid.UUID, user_id: uuid.UUID) -> Optional[Chart]:
    """Get a specific chart by ID (only if user owns it or it's public, or admin)"""
    if user_id is None:  # Admin access
        return db.query(Chart).filter(
            and_(
                Chart.id == chart_id,
                Chart.is_deleted == False
            )
        ).first()
    else:  # Regular user access
        return db.query(Chart).filter(
            and_(
                Chart.id == chart_id,
                Chart.is_deleted == False,
                or_(
                    Chart.user_id == user_id,
                    Chart.visibility == "public"
                )
            )
        ).first()

def update_chart(db: Session, chart_id: uuid.UUID, user_id: uuid.UUID, chart_update: ChartUpdate) -> Optional[Chart]:
    """Update a chart"""
    chart = get_chart_by_id(db, chart_id, user_id)
    if not chart:
        return None
    
    # Only owner or admin can update
    if user_id is not None and chart.user_id != user_id:
        return None
    
    update_data = chart_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(chart, field, value)
    
    chart.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(chart)
    return chart

def delete_chart(db: Session, chart_id: uuid.UUID, user_id: uuid.UUID) -> bool:
    """Soft delete a chart"""
    chart = get_chart_by_id(db, chart_id, user_id)
    if not chart:
        return False
    
    # Only owner or admin can delete
    if user_id is not None and chart.user_id != user_id:
        return False
    
    chart.is_deleted = True
    chart.updated_at = datetime.utcnow()
    db.commit()
    return True

def bulk_delete_charts(db: Session, chart_ids: List[uuid.UUID], user_id: uuid.UUID) -> int:
    """Bulk delete charts"""
    deleted_count = db.query(Chart).filter(
        and_(
            Chart.id.in_(chart_ids),
            Chart.user_id == user_id,
            Chart.is_deleted == False
        )
    ).update({
        "is_deleted": True,
        "updated_at": datetime.utcnow()
    })
    
    db.commit()
    return deleted_count

def get_chart_count(db: Session, user_id: uuid.UUID) -> int:
    """Get total chart count for user"""
    return db.query(Chart).filter(
        and_(
            Chart.user_id == user_id,
            Chart.is_deleted == False
        )
    ).count()

def search_charts(
    db: Session, 
    user_id: uuid.UUID, 
    search_term: str,
    skip: int = 0,
    limit: int = 100
) -> List[Chart]:
    """Search charts by label, description, or tags"""
    return db.query(Chart).filter(
        and_(
            Chart.user_id == user_id,
            Chart.is_deleted == False,
            or_(
                Chart.label.ilike(f"%{search_term}%"),
                Chart.description.ilike(f"%{search_term}%"),
                Chart.tags.any(search_term)
            )
        )
    ).offset(skip).limit(limit).all()

def get_all_charts(
    db: Session, 
    skip: int = 0, 
    limit: int = 100
) -> List[Chart]:
    """Get all charts (admin only)"""
    return db.query(Chart).filter(
        Chart.is_deleted == False
    ).offset(skip).limit(limit).all()

def get_all_charts_count(db: Session) -> int:
    """Get total charts count (admin only)"""
    return db.query(Chart).filter(
        Chart.is_deleted == False
    ).count() 