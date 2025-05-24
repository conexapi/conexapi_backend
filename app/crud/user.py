# Ubicación: /conexapi/conexapi_backend/app/crud/user.py
# Propósito: Contiene las operaciones de base de datos (Crear, Leer, Actualizar, Borrar - CRUD)
#            específicas para el modelo de usuario.
# Dependencias: sqlalchemy.orm.Session, app.database.models.User, app.schemas.user.UserCreate, passlib.hash.bcrypt

from sqlalchemy.orm import Session
from app.database import models
from app.schemas import user as schemas_user
from passlib.context import CryptContext

# Propósito: Objeto para manejar el cifrado (hashing) y verificación de contraseñas.
#            Utiliza el algoritmo bcrypt, que es seguro y recomendado.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    # Propósito: Cifra una contraseña en texto plano para almacenarla de forma segura.
    # Parámetros:
    #   - password (str): La contraseña en texto plano que se va a cifrar.
    # Retorno:
    #   - (str): La contraseña cifrada (hashed).
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Propósito: Verifica si una contraseña en texto plano coincide con una contraseña cifrada.
    # Parámetros:
    #   - plain_password (str): La contraseña que el usuario intentó ingresar (texto plano).
    #   - hashed_password (str): La contraseña cifrada que está almacenada en la base de datos.
    # Retorno:
    #   - (bool): True si las contraseñas coinciden, False en caso contrario.
    return pwd_context.verify(plain_password, hashed_password)

def get_user_by_email(db: Session, email: str):
    # Propósito: Busca un usuario en la base de datos por su dirección de correo electrónico.
    # Parámetros:
    #   - db (Session): La sesión de la base de datos activa.
    #   - email (str): La dirección de correo electrónico del usuario a buscar.
    # Retorno:
    #   - (models.User | None): El objeto User si se encuentra, None si no existe.
    # : (dos puntos): Indica la anotación de tipo para los parámetros de la función.
    # | None (Pipe None): Símbolo que indica que la función puede retornar un objeto User O None.
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas_user.UserCreate):
    # Propósito: Crea un nuevo usuario en la base de datos.
    # Parámetros:
    #   - db (Session): La sesión de la base de datos activa.
    #   - user (schemas_user.UserCreate): Un objeto UserCreate con los datos del nuevo usuario
    #                                      (email y contraseña en texto plano).
    # Retorno:
    #   - (models.User): El objeto User recién creado y guardado en la base de datos.

    hashed_password = get_password_hash(user.password)
    # hashed_password (str): Almacena la contraseña cifrada.

    # Símbolo especial: **user.model_dump()
    # **kwargs: El doble asterisco (**) en **user.model_dump() es el operador de desempaquetado de diccionario.
    #           Toma un diccionario (el resultado de user.model_dump(), que convierte el esquema Pydantic
    #           en un diccionario) y lo pasa como argumentos de palabra clave a la función o constructor.
    #           Aquí, pasa 'email' y 'password' (que luego es reemplazado por 'hashed_password')
    #           al constructor del modelo User de SQLAlchemy.
    db_user = models.User(email=user.email, hashed_password=hashed_password)

    db.add(db_user) # Añade el nuevo objeto User a la sesión de la base de datos.
    db.commit()     # Guarda los cambios (el nuevo usuario) en la base de datos.
    db.refresh(db_user) # Actualiza el objeto db_user con los datos generados por la DB (como el ID).
    # -> (models.User): La flecha indica que esta función retorna un objeto de tipo models.User.
    return db_user