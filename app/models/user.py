from sqlalchemy import Column, String, Boolean, Date, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from db.base import Base
import uuid

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String)
    full_name = Column(String)
    birthdate = Column(Date)
    is_premium = Column(Boolean, default=False)
    role = Column(String, default="user")  # "user", "admin", "premium"
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    charts = relationship("Chart", back_populates="user")
    subscriptions = relationship("Subscription", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
    progress = relationship("UserProgress", back_populates="user", uselist=False)
    tasks = relationship("UserTask", back_populates="user")
    events = relationship("UserEvent", back_populates="user")
    api_keys = relationship("ApiKey", back_populates="user")
    preferences = relationship("UserPreference", back_populates="user", uselist=False)