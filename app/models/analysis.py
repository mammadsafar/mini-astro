from sqlalchemy import Column, String, DateTime, Text, Date
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from db.base import Base
import uuid

class ChartAnalysis(Base):
    __tablename__ = "chart_analyses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chart_id = Column(UUID(as_uuid=True), ForeignKey("charts.id"))
    analysis_type = Column(String)  # 'natal' | 'transit' | 'composite' | 'synastry'
    analysis_text = Column(Text)
    pdf_url = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    chart = relationship("Chart", back_populates="analyses")

class CompositeChart(Base):
    __tablename__ = "composite_charts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chart1_id = Column(UUID(as_uuid=True), ForeignKey("charts.id"))
    chart2_id = Column(UUID(as_uuid=True), ForeignKey("charts.id"))
    chart_json = Column(JSONB)
    chart_svg_url = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    chart1 = relationship("Chart", foreign_keys=[chart1_id], back_populates="composite_charts_1")
    chart2 = relationship("Chart", foreign_keys=[chart2_id], back_populates="composite_charts_2")

class DailyTransit(Base):
    __tablename__ = "daily_transits"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chart_id = Column(UUID(as_uuid=True), ForeignKey("charts.id"))
    date = Column(Date)
    analysis_text = Column(Text)
    suggested_tasks = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    chart = relationship("Chart", back_populates="daily_transits") 