from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from db.base import Base
import uuid

class UserPreference(Base):
    __tablename__ = "user_preferences"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True)
    
    # Notification preferences
    email_notifications = Column(Boolean, default=True)
    push_notifications = Column(Boolean, default=True)
    in_app_notifications = Column(Boolean, default=True)
    
    # Notification types
    daily_task_notifications = Column(Boolean, default=True)
    transit_warning_notifications = Column(Boolean, default=True)
    new_article_notifications = Column(Boolean, default=True)
    level_up_notifications = Column(Boolean, default=True)
    
    # Other preferences
    language = Column(String, default="fa")  # "fa", "en"
    timezone = Column(String, default="Asia/Tehran")
    theme = Column(String, default="light")  # "light", "dark"
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="preferences") 