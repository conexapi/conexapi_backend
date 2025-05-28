# Ubicación: /conexapi/conexapi_backend/app/api/users.py
# Propósito: Define los endpoints de la API para la gestión de usuarios,
#            incluyendo registro, obtención de perfil, y operaciones CRUD
#            (Crear, Leer, Actualizar, Eliminar) para usuarios.
# Dependencias: fastapi, sqlalchemy.orm.Session, app.database.database,
#               app.crud.user, app.schemas.user, app.utils.auth

from typing import Annotated, List # <-- Asegúrate que List está importado
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.crud import user as crud_user
from app.schemas import user as schemas_user
from app.utils.auth import get_current_user, is_admin, is_regular_user # <-- Asegúrate de importar is_admin y is_regular_user

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

# Endpoint para crear un nuevo usuario (registro)
@router.post(
    "/",
    response_model=schemas_user.UserInDB,
    status_code=status.HTTP_201_CREATED,
    summary="Registra un nuevo usuario",
    response_description="Usuario registrado exitosamente."
)
async def create_user(
    user: schemas_user.UserCreate,
    db: Session = Depends(get_db)
):
    db_user = crud_user.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo electrónico ya está registrado."
        )
    return crud_user.create_user(db=db, user=user)

# Endpoint para obtener el perfil del usuario actual (requiere autenticación)
@router.get(
    "/me",
    response_model=schemas_user.UserInDB,
    summary="Obtiene el perfil del usuario actual",
    response_description="Perfil del usuario autenticado."
)
async def read_users_me(
    current_user: Annotated[schemas_user.UserInDB, Depends(get_current_user)]
):
    return current_user

# Endpoint para obtener todos los usuarios (solo administradores)
@router.get(
    "/",
    response_model=List[schemas_user.UserInDB],
    summary="Obtiene todos los usuarios (solo administradores)",
    response_description="Lista de todos los usuarios registrados."
)
async def read_users(   
    current_admin_user: Annotated[schemas_user.UserInDB, Depends(is_admin())], # Protegido por admin
    db: Session = Depends(get_db),
     skip: int = 0, limit: int = 100
):
    users = crud_user.get_users(db, skip=skip, limit=limit)
    return users

# Endpoint para obtener un usuario por ID (solo administradores)
@router.get(
    "/{user_id}",
    response_model=schemas_user.UserInDB,
    summary="Obtiene un usuario por ID (solo administradores)",
    response_description="Usuario encontrado por ID."
)
async def read_user(
    user_id: int,
    current_admin_user: Annotated[schemas_user.UserInDB, Depends(is_admin())], # Protegido por admin
    db: Session = Depends(get_db)
):
    db_user = crud_user.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    return db_user

# Endpoint para actualizar un usuario (solo administradores)
@router.patch(
    "/{user_id}",
    response_model=schemas_user.UserInDB,
    summary="Actualiza un usuario por ID (solo administradores)",
    response_description="Usuario actualizado exitosamente."
)
async def update_user(
    user_id: int,
    user_update: schemas_user.UserUpdate, # Asumo que tienes un UserUpdate schema en user.py
    current_admin_user: Annotated[schemas_user.UserInDB, Depends(is_admin())], # Protegido por admin
    db: Session = Depends(get_db)
):
    # crud_user.update_user debe ser actualizado para usar UserUpdate schema y Pydantic model_dump
    updated_user = crud_user.update_user(db=db, user_id=user_id, user_update=user_update)
    if updated_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    return updated_user

# Endpoint para eliminar un usuario (solo administradores)
@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Elimina un usuario por ID (solo administradores)",
    response_description="Usuario eliminado exitosamente."
)
async def delete_user(
    user_id: int,
    current_admin_user: Annotated[schemas_user.UserInDB, Depends(is_admin())], # Protegido por admin
    db: Session = Depends(get_db)
):
    db_user = crud_user.delete_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    # No devuelve nada en 204 No Content
    return {"message": "Usuario eliminado exitosamente"}

# Si tienes un endpoint para 'admin-only', puedes mantenerlo, pero no es parte del CRUD estándar.
# @router.get("/admin-only")
# async def read_admin_data(current_admin_user: Annotated[schemas_user.UserInDB, Depends(is_admin())]):
#     return {"message": f"¡Hola, administrador {current_admin_user.email}! Esta es data secreta."}