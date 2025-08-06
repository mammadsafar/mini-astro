from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.config import settings

# Create engine for PostgreSQL
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)