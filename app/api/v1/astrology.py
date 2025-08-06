from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from core.dependencies import get_db
from schemas.chart import AstroInput, AstroPairInput, ChartCreate, ChartOut
from services import astro_service
from typing import List
import uuid

router = APIRouter()

@router.post("/chart-json", summary="Generate Natal Chart (JSON)")
def get_astrological_chart(data: AstroInput):
    """Returns detailed natal chart as JSON including planets, houses, elements, and aspects."""
    return astro_service.generate_natal_chart(data)

@router.post("/chart-svg", summary="Generate Natal Chart SVG")
def generate_chart_svg(data: AstroInput):
    """Returns natal chart as an SVG image."""
    filename = astro_service.generate_chart_svg(data)
    
    def iterfile():
        with open(filename, "rb") as f:
            yield from f

    return StreamingResponse(iterfile(), media_type="image/svg+xml")

@router.post("/report", summary="Full Natal Report")
def get_full_report(data: AstroInput):
    """Returns a full natural language report based on the natal chart."""
    report = astro_service.generate_full_report(data)
    return {"report": report}

@router.post("/synastry", summary="Synastry Aspects")
def get_synastry_aspects(data: AstroPairInput):
    """Returns relationship aspects between two birth charts."""
    aspects = astro_service.generate_synastry_aspects(data)
    return {"aspects": aspects}

@router.post("/relationship-score", summary="Relationship Score")
def get_relationship_score(data: AstroPairInput):
    """Returns a compatibility score and explanation for a pair of charts."""
    score = astro_service.generate_relationship_score(data)
    return score

@router.post("/composite", summary="Composite Chart")
def get_composite_chart(data: AstroPairInput):
    """Returns composite chart (combined energy) for two birth charts."""
    composite = astro_service.generate_composite_chart(data)
    return composite

@router.post("/charts/", response_model=ChartOut)
def create_chart(chart: ChartCreate, db: Session = Depends(get_db)):
    """Create a new chart for the current user"""
    # TODO: Get current user from authentication
    # For now, using a placeholder user_id
    user_id = uuid.uuid4()  # This should come from authentication
    
    # Convert chart data to AstroInput format
    astro_input = AstroInput(
        name=chart.label,
        year=chart.birth_date.year,
        month=chart.birth_date.month,
        day=chart.birth_date.day,
        hour=chart.birth_time.hour,
        minute=chart.birth_time.minute,
        lat=0.0,  # TODO: Add to ChartCreate schema
        lng=0.0,  # TODO: Add to ChartCreate schema
        city=chart.birth_place,
        tz_str="UTC"  # TODO: Add to ChartCreate schema
    )
    
    chart_data = astro_service.generate_natal_chart(astro_input)
    saved_chart = astro_service.save_chart_to_db(
        db, user_id, chart_data, chart.label, 
        chart.birth_date, chart.birth_time, chart.birth_place
    )
    return saved_chart

@router.get("/charts/", response_model=List[ChartOut])
def get_user_charts(db: Session = Depends(get_db)):
    """Get all charts for the current user"""
    # TODO: Get current user from authentication
    user_id = uuid.uuid4()  # This should come from authentication
    return astro_service.get_user_charts(db, user_id)

@router.get("/charts/{chart_id}", response_model=ChartOut)
def get_chart(chart_id: uuid.UUID, db: Session = Depends(get_db)):
    """Get a specific chart by ID"""
    chart = astro_service.get_chart_by_id(db, chart_id)
    if not chart:
        raise HTTPException(status_code=404, detail="Chart not found")
    return chart 