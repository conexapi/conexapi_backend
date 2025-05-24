# Ubicación: /conexapi/backend/app/auth.py
# Propósito: Contiene funciones de utilidad para el hashing de contraseñas,
#              creación y verificación de JWTs, y manejo de errores de autenticación.

# Dependencias: passlib (para bcrypt), python-jose (para JWT), datetime, timedelta, os, HTTPException,
#               SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES del .env

from datetime import datetime, timedelta, timezone # Para manejar fechas y tiempos (expiración de tokens)
from typing import Optional # Para tipos que pueden ser opcionales
from jose import JWTError, jwt # jose: Librería para JWT (JSON Web Tokens)
from passlib.context import CryptContext # passlib: Para hashing de contraseñas
from fastapi import HTTPException, status # FastAPI: Para manejar errores HTTP
from fastapi.security import OAuth2PasswordBearer # FastAPI: Esquema de seguridad para autenticación con contraseña y token
from dotenv import load_dotenv
import os

# Cargar las variables de entorno para las configuraciones JWT
load_dotenv()

# Obtener las variables de entorno JWT.
# Levantamos un error si no están configuradas, porque son esenciales para la seguridad.
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES_STR = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")

if not SECRET_KEY:
    raise ValueError("SECRET_KEY no está configurada en el archivo .env")
if not ALGORITHM:
    raise ValueError("ALGORITHM no está configurada en el archivo .env")
if not ACCESS_TOKEN_EXPIRE_MINUTES_STR:
    raise ValueError("ACCESS_TOKEN_EXPIRE_MINUTES no está configurada en el archivo .env")

# Convertir la duración del token a un número entero
ACCESS_TOKEN_EXPIRE_MINUTES = int(ACCESS_TOKEN_EXPIRE_MINUTES_STR)

# Configurar el contexto de hashing de contraseñas.
# CryptContext(schemes=["bcrypt"], deprecated="auto"): Le dice a passlib que use Bcrypt
# para hashear contraseñas y que maneje automáticamente algoritmos en desuso.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configurar OAuth2PasswordBearer para la autenticación de tokens.
# tokenUrl="token": Es la URL donde los clientes enviarán sus credenciales para obtener un token.
#                    Esto se usa para la documentación de Swagger/OpenAPI.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# --- Funciones de Hashing y Verificación de Contraseñas ---

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica si una contraseña en texto plano coincide con una contraseña hasheada.

    Args:
        plain_password (str): La contraseña que el usuario ha introducido (texto plano).
        hashed_password (str): La contraseña hasheada almacenada en la base de datos.

    Returns:
        bool: True si las contraseñas coinciden, False en caso contrario.
    """
    # pwd_context.verify(plain_password, hashed_password): Utiliza bcrypt para comparar
    # la contraseña en texto plano con el hash.
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Genera un hash seguro para una contraseña en texto plano.

    Args:
        password (str): La contraseña en texto plano a hashear.

    Returns:
        str: La contraseña hasheada.
    """
    # pwd_context.hash(password): Utiliza bcrypt para hashear la contraseña.
    return pwd_context.hash(password)

# --- Funciones para JWT (JSON Web Tokens) ---

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crea un nuevo token de acceso JWT.

    Args:
        data (dict): Un diccionario con los datos a codificar en el token (ej. {"sub": "user@example.com"}).
        expires_delta (Optional[timedelta]): La duración opcional del token. Si es None, usa la duración por defecto.

    Returns:
        str: El token JWT codificado.
    """
    # Copiamos los datos para no modificar el diccionario original.
    to_encode = data.copy()

    # Define el tiempo de expiración del token.
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        # Si no se especifica duración, usa la por defecto del .env
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    # Añade el tiempo de expiración al diccionario de datos.
    to_encode.update({"exp": expire})

    # Codifica el token usando los datos, la clave secreta y el algoritmo.
    # jwt.encode(payload, key, algorithm): Codifica el JWT.
    # payload: Los datos a incluir (el diccionario to_encode).
    # key: La clave secreta para firmar el token.
    # algorithm: El algoritmo de encriptación.
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> dict:
    """
    Decodifica y verifica un token JWT.

    Args:
        token (str): El token JWT a decodificar.

    Returns:
        dict: Los datos decodificados del token.

    Raises:
        HTTPException: Si el token no es válido o ha expirado.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, # Código de estado HTTP 401: No autorizado
        detail="No se pudieron validar las credenciales", # Mensaje de error
        headers={"WWW-Authenticate": "Bearer"}, # Encabezado para indicar el tipo de autenticación
    )
    try:
        # jwt.decode(token, key, algorithms): Decodifica el JWT.
        # options={"verify_aud": False}: Desactiva la verificación de la audiencia,
        # lo cual es útil si no estamos usando un campo 'aud' específico.
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_aud": False})
        return payload
    except JWTError: # Si el token no es válido (ej. firma incorrecta, formato inválido)
        raise credentials_exception
    except Exception as e: # Cualquier otro error inesperado
        print(f"Error inesperado al decodificar token: {e}")
        raise credentials_exception

# Símbolos especiales explicados:
# `-> bool`: Anotación de tipo que indica que la función retornará un valor booleano.
# `Optional[timedelta]`: Indica que el argumento `expires_delta` puede ser un objeto `timedelta` o `None`.
# `timedelta`: Objeto de `datetime` que representa una duración de tiempo.
# `jwt.encode`, `jwt.decode`: Funciones de la librería `python-jose` para manejar JWTs.
# `HTTPException`: Clase de FastAPI para levantar errores HTTP específicos que la API puede manejar.
# `status.HTTP_401_UNAUTHORIZED`: Una constante de FastAPI para el código de estado HTTP 401.
# `payload`: En JWT, el "payload" es la sección donde se guardan los datos.