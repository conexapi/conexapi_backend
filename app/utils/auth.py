# Ubicación: /conexapi/conexapi_backend/app/utils/auth.py
# Propósito: Contiene funciones de utilidad para la verificación de tokens JWT y la gestión de usuarios.
#            Aquí decodificaremos el token y obtendremos el usuario asociado a él.
# Dependencias: datetime, typing, jose.jwt, fastapi, sqlalchemy.orm.Session,
#               app.config, app.database.database, app.crud.user, app.schemas.user

from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from app.config import settings
from app.database.database import get_db
from app.crud import user as crud_user
from app.schemas import user as schemas_user

# Propósito: Objeto para manejar la seguridad OAuth2 con token Bearer.
#            Define el esquema de seguridad que FastAPI usará para esperar un token.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], # Obtiene el token de la cabecera Authorization
    db: Session = Depends(get_db) # Obtiene una sesión de base de datos
) -> schemas_user.UserInDB:
    # Propósito: Decodifica un token JWT, verifica su validez y devuelve el usuario asociado.
    #            Es el "guardián" de nuestros endpoints protegidos.
    # Parámetros:
    #   - token (str): El token JWT recibido en la cabecera 'Authorization'.
    #   - db (Session): Sesión de base de datos para buscar al usuario.
    # Retorno:
    #   - (schemas_user.UserInDB): El objeto UserInDB si el token es válido y el usuario existe.
    # Excepciones:
    #   - HTTPException (401 Unauthorized): Si el token es inválido, ha expirado o el usuario no se encuentra.

    # 1. Definir credenciales de excepción para errores de autenticación.
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # 2. Decodificar el token.
        # jwt.decode(): Intenta decodificar el token usando la clave secreta y el algoritmo.
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        # "sub": Extrae el "subject" (generalmente el email del usuario) del payload del token.
        username: str = payload.get("sub")
        if username is None:
            # Si no hay "sub" en el token, no es válido.
            raise credentials_exception
        # 3. Validar el esquema del token con Pydantic (opcional pero buena práctica).
        token_data = schemas_user.TokenData(username=username) # Usa un esquema de token (lo crearemos en el siguiente paso)
    except JWTError:
        # Si hay un error al decodificar el token (ej. firma inválida, expirado).
        raise credentials_exception

    # 4. Buscar el usuario en la base de datos usando el email del token.
    user = crud_user.get_user_by_email(db, email=token_data.username)
    if user is None:
        # Si el usuario no existe en la base de datos (quizás fue eliminado después de emitir el token).
        raise credentials_exception

    # 5. Si todo es válido, devolvemos el objeto del usuario.
    return schemas_user.UserInDB.from_orm(user)