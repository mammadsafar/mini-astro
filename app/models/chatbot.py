from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from db.base import Base
import uuid

class Chatbot(Base):
    __tablename__ = "chatbots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chart_id = Column(UUID(as_uuid=True), ForeignKey("charts.id"))
    title = Column(String)
    prompt = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    chart = relationship("Chart", back_populates="chatbots")
    messages = relationship("ChatbotMessage", back_populates="chatbot")

class ChatbotMessage(Base):
    __tablename__ = "chatbot_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chatbot_id = Column(UUID(as_uuid=True), ForeignKey("chatbots.id"))
    role = Column(String)  # 'user' or 'bot'
    message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    chatbot = relationship("Chatbot", back_populates="messages") 