from sqlalchemy import Column, String, Date, Time, DateTime, Text, Float, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.sql import func
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from db.base import Base
import uuid

class Chart(Base):
    __tablename__ = "charts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Basic chart info
    label = Column(String, nullable=False)  # "من", "مامان", "پارتنر"
    category = Column(String)  # "self", "friend", "partner", "client"
    chart_type = Column(String, nullable=False)  # "natal", "composite", "transit", "synastry"
    visibility = Column(String, default="private")  # "private", "public"
    
    # Birth data
    birth_date = Column(Date, nullable=False)
    birth_time = Column(Time, nullable=False)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    city = Column(String, nullable=False)
    timezone = Column(String, nullable=False)  # "Asia/Tehran"
    timezone_offset = Column(String)  # "+03:30" or "+3.5"
    
    # Chart data
    chart_json = Column(JSONB)
    chart_svg_url = Column(Text)
    source_api = Column(String, default="swiss_ephemeris")
    
    # Additional fields
    description = Column(Text)
    notes = Column(Text)
    tags = Column(ARRAY(String))
    
    # Soft delete
    is_deleted = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="charts")
    analyses = relationship("ChartAnalysis", back_populates="chart")
    composite_charts_1 = relationship("CompositeChart", foreign_keys="CompositeChart.chart1_id", back_populates="chart1")
    composite_charts_2 = relationship("CompositeChart", foreign_keys="CompositeChart.chart2_id", back_populates="chart2")
    daily_transits = relationship("DailyTransit", back_populates="chart")
    chatbots = relationship("Chatbot", back_populates="chart") 