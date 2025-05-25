# Ubicación: /conexapi/conexapi_backend/app/crud/user.py

from sqlalchemy.orm import Session
from sqlalchemy import select
from app.database import models # <-- Aquí importamos los modelos, no la función de crear tablas
from app.schemas import user as schemas_user
from passlib.context import CryptContext

# ELIMINA ESTA LÍNEA SI ESTÁ PRESENTE:
# from app.database.models import create_db_and_tables # <-- ¡ELIMINAR ESTA LÍNEA!

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_user_by_email(db: Session, email: str):
    return db.scalar(select(models.User).where(models.User.email == email))

def create_user(db: Session, user: schemas_user.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user