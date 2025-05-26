# Ubicación: /conexapi/conexapi_backend/app/api/users.py
# Propósito: Define endpoints de ejemplo que requieren autenticación (un token JWT válido).
# Dependencias: fastapi, app.utils.auth, app.schemas.user

from typing import Annotated

from fastapi import APIRouter, Depends
from app.schemas import user as schemas_user
from app.utils.auth import get_current_user # <-- ¡NUEVA LÍNEA!

# Propósito: Crea un router de FastAPI para organizar los endpoints relacionados con los usuarios.
router = APIRouter(
    prefix="/users", # Prefijo para todas las rutas en este router (ej. /users/me)
    tags=["Users"]   # Etiqueta para agrupar en la documentación de Swagger UI.
)

@router.get("/me", response_model=schemas_user.UserInDB)
async def read_users_me(
    current_user: Annotated[schemas_user.UserInDB, Depends(get_current_user)]
):
    # Propósito: Endpoint de ejemplo para obtener información del usuario autenticado.
    #            Solo accesible si se proporciona un token JWT válido.
    # Parámetros:
    #   - current_user (schemas_user.UserInDB): Inyectado por FastAPI después de que
    #     get_current_user verifica el token y obtiene el usuario de la DB.
    # Retorno:
    #   - (schemas_user.UserInDB): El objeto UserInDB del usuario actualmente autenticado.
    return current_user