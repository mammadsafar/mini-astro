from sqlalchemy import Column, String, DateTime, Boolean, Integer, Date, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from db.base import Base
import uuid

class UserProgress(Base):
    __tablename__ = "user_progress"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    xp = Column(Integer, default=0)
    level = Column(Integer, default=1)
    updated_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="progress")

class UserTask(Base):
    __tablename__ = "user_tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    date = Column(Date)
    description = Column(Text)
    completed = Column(Boolean, default=False)

    # Relationships
    user = relationship("User", back_populates="tasks")

class UserEvent(Base):
    __tablename__ = "user_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    event_type = Column(String)
    event_metadata = Column(JSONB)
    occurred_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="events") 