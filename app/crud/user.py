# Ubicación: /conexapi/conexapi_backend/app/crud/user.py
from typing import Optional, Sequence
from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete 
from app.database import models # <-- Aquí importamos los modelos, no la función de crear tablas
from app.schemas import user as schemas_user
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_user_by_email(db: Session, email: str):
    return db.scalar(select(models.User).where(models.User.email == email))

def get_users(db: Session, skip: int = 0, limit: int = 100) -> Sequence[models.User]:
    return db.scalars(select(models.User).offset(skip).limit(limit)).all()

def get_user(db: Session, user_id: int) -> Optional[models.User]:
    return db.scalar(select(models.User).where(models.User.id == user_id))

def create_user(db: Session, user: schemas_user.UserCreate):
    hashed_password = get_password_hash(user.password)

    # Crear el objeto User con el email, la contraseña cifrada y el rol por defecto.
    # No pasamos 'role' directamente de user: schemas_user.UserCreate,
    # porque UserCreate no tiene un campo 'role' (y el modelo ya tiene un valor por defecto).
    db_user = models.User(email=user.email, hashed_password=hashed_password, role="regular")
    # Si UserCreate tuviera un campo role y se quisiera usar, sería:
    # db_user = models.User(email=user.email, hashed_password=hashed_password, role=user.role)
    # Pero por ahora, forzamos el rol "regular" para nuevos registros.
   
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user_update: schemas_user.UserUpdate) -> Optional[models.User]:
    db_user = get_user(db, user_id)
    if db_user:
        update_data = user_update.model_dump(exclude_unset=True)
        if update_data:
            # Hash la nueva contraseña si se proporciona
            if "password" in update_data:
                update_data["hashed_password"] = get_password_hash(update_data.pop("password"))

            stmt = update(models.User).where(models.User.id == user_id).values(**update_data)
            db.execute(stmt)
            db.commit()
            db.refresh(db_user) # Refrescar para obtener los datos actualizados
    return db_user

def delete_user(db: Session, user_id: int) -> Optional[models.User]:
    db_user = get_user(db, user_id)
    if db_user:
        stmt = delete(models.User).where(models.User.id == user_id)
        db.execute(stmt)
        db.commit()
        return db_user # Devuelve el objeto que fue eliminado
    return None