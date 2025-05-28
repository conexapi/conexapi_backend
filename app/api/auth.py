# Ubicación: /conexapi/conexapi_backend/app/api/auth.py
# Propósito: Define los endpoints de la API para el registro y la autenticación de usuarios.
# Dependencias: fastapi, sqlalchemy.orm.Session, datetime, timedelta, jwt, app.config,
#               app.database.database, app.crud.user, app.schemas.user,
#               fastapi.security.OAuth2PasswordRequestForm

from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from app.database.database import get_db
from app.crud import user as crud_user
from app.schemas import user as schemas_user
from app.config import settings # Importar la configuración que incluye SECRET_KEY y ALGORITHM

# Propósito: Crea un router de FastAPI para organizar los endpoints relacionados con la autenticación.
#            Es como agrupar todas las "ventanillas" de seguridad en un solo lugar.
router = APIRouter(
    prefix="/auth", # Prefijo para todas las rutas en este router (ej. /auth/register)
    tags=["Auth"]   # Etiqueta para agrupar en la documentación de Swagger UI.
)

# Propósito: Objeto para manejar la seguridad OAuth2 con contraseña.
#            Le dice a FastAPI cómo esperar un token de autenticación en la cabecera 'Authorization'.
# /token (str): La ruta donde el cliente debe enviar la contraseña para obtener el token.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    # Propósito: Genera un token JWT (JSON Web Token) con una duración determinada.
    # Parámetros:
    #   - data (dict): Los datos que se incluirán en el token (ej. el email del usuario).
    #   - expires_delta (timedelta | None): El tiempo de expiración del token.
    # Retorno:
    #   - (str): El token JWT codificado.
    # Símbolo especial: | None (Pipe None): Indica que expires_delta puede ser un objeto timedelta o None.
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        # Si no se especifica, usa el tiempo de expiración de la configuración.
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire}) # Agrega la fecha de expiración al token.
    # Símbolo especial: jwt.encode(). Codifica los datos en un JWT usando la clave secreta y el algoritmo.
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

@router.post("/register", response_model=schemas_user.UserInDB)
async def register_user(
    user: schemas_user.UserCreate, # Recibe los datos del usuario (email, password)
    db: Session = Depends(get_db)  # Obtiene una sesión de base de datos
):
    # Propósito: Endpoint para que un nuevo usuario se registre en el sistema.
    # Responsabilidades: Validar datos, verificar si el email ya existe, crear usuario y devolverlo.

    # 1. Verificar si el email ya está registrado.
    db_user = crud_user.get_user_by_email(db, email=user.email)
    if db_user:
        # Si el email ya existe, lanzamos una excepción HTTP con un código de estado 400.
        # : (dos puntos): En este contexto, parte de la sintaxis de excepción.
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email ya registrado"
        )
    # 2. Si el email no existe, creamos el usuario en la base de datos.
    return crud_user.create_user(db=db, user=user)

@router.post("/token", response_model=dict)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], # Recibe username y password de un formulario
    db: Session = Depends(get_db) # Obtiene una sesión de base de datos
):
    # Propósito: Endpoint para que un usuario inicie sesión y obtenga un token de acceso JWT.
    # Responsabilidades: Validar credenciales, generar y devolver el token.

    user_email = form_data.username # OAuth2PasswordRequestForm usa 'username' para el identificador
    user_password = form_data.password

    # 1. Buscar al usuario por email.
    user = crud_user.get_user_by_email(db, email=user_email)
    if not user:
        # Si el usuario no existe, lanzamos una excepción 401 (Unauthorized).
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # 2. Verificar la contraseña.
    if not crud_user.verify_password(user_password, str(user.hashed_password)):
        # Si la contraseña no coincide, lanzamos una excepción 401.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # 3. Si las credenciales son correctas, creamos el token de acceso.
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, # "sub" (subject) es una convención JWT para el identificador del usuario.
        expires_delta=access_token_expires
    )
    # Retorno:
    # -> dict: La función devuelve un diccionario con el token de acceso y su tipo.
    return {"access_token": access_token, "token_type": "bearer"}