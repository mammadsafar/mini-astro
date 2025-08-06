from sqlalchemy.orm import Session
from models.user import User
from schemas.user import UserCreate, UserUpdate
from passlib.context import CryptContext
from typing import Optional
import uuid

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def create_user(db: Session, user: UserCreate) -> User:
    """Create a new user"""
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        password_hash=hashed_password,
        full_name=user.full_name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user(db: Session, user_id: uuid.UUID) -> Optional[User]:
    """Get user by ID"""
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email"""
    return db.query(User).filter(User.email == email).first()

def get_all_users(db: Session) -> list[User]:
    """Get all users"""
    return db.query(User).all()

def update_user(db: Session, user_id: uuid.UUID, user_update: UserUpdate) -> Optional[User]:
    """Update user information"""
    user = get_user(db, user_id)
    if not user:
        return None
    
    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    return user

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Authenticate user with email and password"""
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user

def get_all_users_paginated(db: Session, skip: int = 0, limit: int = 100) -> list[User]:
    """Get all users with pagination"""
    return db.query(User).filter(User.is_deleted == False).offset(skip).limit(limit).all()

def get_users_count(db: Session) -> int:
    """Get total users count"""
    return db.query(User).filter(User.is_deleted == False).count()

def delete_user(db: Session, user_id: uuid.UUID) -> bool:
    """Soft delete user"""
    user = get_user(db, user_id)
    if not user:
        return False
    
    user.is_deleted = True
    db.commit()
    return True