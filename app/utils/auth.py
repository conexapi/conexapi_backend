# Ubicación: /conexapi/conexapi_backend/app/utils/auth.py
# Propósito: Contiene funciones de utilidad para la verificación de tokens JWT y la gestión de usuarios.
#            Aquí decodificaremos el token y obtendremos el usuario asociado a él.
# Dependencias: datetime, typing, jose.jwt, fastapi, sqlalchemy.orm.Session,
#               app.config, app.database.database, app.crud.user, app.schemas.user

from datetime import datetime, timedelta, timezone
from typing import Annotated, Optional # ¡IMPORTANTE: Optional es necesario aquí!

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
#            tokenUrl="/auth/token" indica a FastAPI dónde el cliente puede obtener un token.
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
        
        # Obtener 'sub' (subject) del payload. Puede ser None si no está presente.
        username: Optional[str] = payload.get("sub") 
        
        # 3. Verificar si el username se pudo extraer y es una cadena de texto.
        if username is None:
            raise credentials_exception
        
        # Pylance es estricto, así que aseguramos que es un str antes de pasarlo a Pydantic.
        # Aunque después de 'if username is None' ya sabemos que no es None, 
        # esta comprobación extra ayuda al analizador estático de Pylance.
        if not isinstance(username, str):
            raise credentials_exception

        # Crear un objeto TokenData con el username extraído.
        token_data = schemas_user.TokenData(username=username)
        
    except JWTError:
        # Si hay un error al decodificar el token (ej. firma inválida, expirado),
        # lanzamos una excepción de credenciales.
        raise credentials_exception

    # 4. Asegurarse de que username no es None antes de pasarlo a get_user_by_email.
    # Esto es para calmar a Pylance, ya que lógicamente ya lo verificamos arriba.
    assert token_data.username is not None, "El nombre de usuario no debería ser None después de la validación del token."

    # 5. Buscar el usuario en la base de datos usando el email del token.
    user = crud_user.get_user_by_email(db, email=token_data.username) # Pylance ahora no se quejará aquí.
    
    # 6. Si el usuario no existe en la base de datos (quizás fue eliminado después de emitir el token).
    if user is None:
        raise credentials_exception

    # 7. Si todo es válido, devolvemos el objeto del usuario.
    return schemas_user.UserInDB.from_orm(user)