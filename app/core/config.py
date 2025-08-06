from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    SQLALCHEMY_DATABASE_URL: str = "postgresql://user:password@localhost/astrology_db"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DEBUG: bool = True
    
    # API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Astrology API"
    
    # CORS
    BACKEND_CORS_ORIGINS: list = ["*"]
    
    # File upload
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB

    class Config:
        env_file = ".env"
        from_attributes = True

settings = Settings()