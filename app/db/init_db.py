from db.base import Base
from db.session import engine
from models import *  # Import all models

def init_db():
    """Initialize database by creating all tables"""
    Base.metadata.create_all(bind=engine)

def drop_db():
    """Drop all tables (for development/testing)"""
    Base.metadata.drop_all(bind=engine)
