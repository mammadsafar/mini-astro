from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from db.base import Base
import uuid

class Article(Base):
    __tablename__ = "articles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String)
    slug = Column(String, unique=True)
    content = Column(Text)
    published_at = Column(DateTime(timezone=True)) 