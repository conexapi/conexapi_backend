# Ubicación: /conexapi/backend/main.py
# Propósito: Punto de entrada principal de nuestra API ConexAPI.
#              Aquí configuraremos FastAPI, la conexión a la base de datos
#              y las rutas de autenticación de usuarios.

# Dependencias: FastAPI, Depends, status, HTTPException, os, load_dotenv,
#               SQLAlchemy (create_async_engine, AsyncSession, sessionmaker, declarative_base, text),
#               app.models (User), app.schemas (UserCreate, Token, TokenData),
#               app.auth (get_password_hash, verify_password, create_access_token, decode_access_token, oauth2_scheme).

from fastapi import FastAPI, Depends, HTTPException, status # Importamos lo necesario de FastAPI
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine # SQLAlchemy asíncrono
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base # Para definir nuestros modelos de base de datos
from sqlalchemy import text # Para ejecutar SQL plano, útil para pruebas
from dotenv import load_dotenv
import os

# Importar los módulos que acabamos de crear
from app.models import User # Nuestro modelo de usuario para la base de datos
from app.schemas import UserCreate, Token, TokenData # Nuestros esquemas para validación de datos
from app.auth import ( # Funciones de autenticación y seguridad
    get_password_hash,
    verify_password,
    create_access_token,
    decode_access_token,
    oauth2_scheme,
)

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Obtener la URL de la base de datos desde las variables de entorno
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL no está configurada en el archivo .env")

# Configuración de SQLAlchemy
engine = create_async_engine(DATABASE_URL, echo=True, future=True, pool_pre_ping=True)
Base = declarative_base() # Base para nuestros modelos declarativos de SQLAlchemy

AsyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession
)

# Función de utilidad para obtener una sesión de base de datos.
async def get_db():
    db = AsyncSessionLocal()
    try:
        yield db
    finally:
        await db.close()

# Creamos una instancia de la aplicación FastAPI.
app = FastAPI(
    title="ConexAPI - Middleware",
    description="Sistema Middleware para integrar Marketplaces (MercadoLibre) y ERPs (Siigo Cloud).",
    version="0.0.1",
    docs_url="/docs",
    redoc_url="/redoc"
)

# --- Eventos de inicio y apagado de la aplicación ---
# Esto es crucial para crear las tablas de la base de datos cuando la app inicia.
@app.on_event("startup")
async def startup_event():
    """
    Función que se ejecuta cuando la aplicación FastAPI se inicia.
    Aquí crearemos todas las tablas de la base de datos si no existen.
    """
    async with engine.begin() as conn: # Abre una conexión asíncrona.
        # await conn.run_sync(Base.metadata.create_all):
        # Le dice al motor de la base de datos que cree todas las tablas
        # definidas en nuestros modelos (User) si aún no existen.
        # 'run_sync' es necesario porque 'create_all' es una operación síncrona en SQLAlchemy.
        await conn.run_sync(Base.metadata.create_all)
    print("Base de datos conectada y tablas creadas/verificadas.")


# --- Rutas de Autenticación ---

@app.post("/register", response_model=Token) # response_model=Token: FastAPI validará que la respuesta tenga el formato del esquema Token.
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Registra un nuevo usuario en el sistema.

    Args:
        user (UserCreate): Los datos del usuario (email y contraseña) enviados en la petición.
                           Pydantic los valida automáticamente según el esquema UserCreate.
        db (AsyncSession): Sesión de la base de datos, inyectada por FastAPI.

    Returns:
        Token: Un token de acceso JWT si el registro es exitoso.

    Raises:
        HTTPException: Si el email ya está registrado.
    """
    # Consulta la base de datos para ver si ya existe un usuario con ese email.
    # db.query(User): Inicia una consulta sobre el modelo User.
    # .filter(User.email == user.email): Añade un filtro para buscar por email.
    # .first(): Intenta obtener el primer resultado.
    existing_user_query = await db.execute(text(f"SELECT id FROM users WHERE email = '{user.email}'"))
    existing_user = existing_user_query.scalar_one_or_none()

    if existing_user:
        # Si el usuario ya existe, levanta un error HTTP 400 Bad Request.
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo electrónico ya está registrado"
        )

    # Hashea la contraseña antes de guardarla. ¡Seguridad primero!
    hashed_password = get_password_hash(user.password)

    # Crea una nueva instancia del modelo User con los datos del usuario.
    db_user = User(email=user.email, hashed_password=hashed_password)

    # Añade el nuevo usuario a la sesión de la base de datos.
    db.add(db_user)
    # Guarda los cambios en la base de datos.
    await db.commit()
    # Refresca el objeto db_user para obtener el ID generado por la base de datos y otros datos.
    await db.refresh(db_user)

    # Crea un token de acceso para el nuevo usuario.
    # "sub": El "subject" del token, generalmente el identificador único del usuario (su email aquí).
    access_token = create_access_token(data={"sub": db_user.email})

    # Retorna el token.
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordBearer = Depends(oauth2_scheme), # Este Depends aquí es para la documentación de Swagger.
                                                              # Para el login real se usa OAuth2PasswordRequestForm
    db: AsyncSession = Depends(get_db)
):
    """
    Permite a un usuario iniciar sesión y obtener un token de acceso JWT.

    Args:
        form_data (OAuth2PasswordRequestForm): Los datos de autenticación (username y password)
                                               enviados desde un formulario.
        db (AsyncSession): Sesión de la base de datos.

    Returns:
        Token: Un token de acceso JWT si las credenciales son válidas.

    Raises:
        HTTPException: Si las credenciales son incorrectas.
    """
    # Importamos OAuth2PasswordRequestForm aquí para evitar la importación cíclica
    # (schemas -> main -> auth -> main, etc.).
    from fastapi.security import OAuth2PasswordRequestForm

    # FastAPI inyecta los datos del formulario de login en `form_data`.
    # form_data.username se mapea a nuestro email.
    # form_data.password es la contraseña en texto plano.

    # Buscamos el usuario en la base de datos por su email.
    # db.query(User).filter(User.email == form_data.username).first():
    # Esta es una forma síncrona de consulta. Para asíncrono, necesitamos 'text' o el ORM asíncrono completo.
    # Vamos a usar text por simplicidad, pero lo ideal sería una consulta de SQLAlchemy más robusta.
    user_query = await db.execute(text(f"SELECT * FROM users WHERE email = '{form_data.username}'"))
    user = user_query.scalar_one_or_none() # Obtiene el objeto User si existe, None si no.

    # Si el usuario no existe o la contraseña no coincide, levantamos un error de credenciales.
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Creamos un token de acceso para el usuario autenticado.
    access_token = create_access_token(data={"sub": user.email})

    return {"access_token": access_token, "token_type": "bearer"}


# --- Ruta Protegida de Ejemplo ---

@app.get("/users/me")
async def read_users_me(current_user: User = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    """
    Endpoint de ejemplo para obtener información del usuario autenticado.
    Solo accesible con un token JWT válido.

    Args:
        current_user (User): El usuario autenticado, inyectado por la dependencia de OAuth2.
                             FastAPI y nuestra lógica de auth se encargan de decodificar el token
                             y obtener la información del usuario.
        db (AsyncSession): Sesión de la base de datos.

    Returns:
        dict: Un diccionario con el email del usuario.

    Raises:
        HTTPException: Si no hay un token válido presente.
    """
    # En un caso real, 'current_user' sería el objeto de usuario completo de la DB.
    # Aquí, oauth2_scheme nos da el token, y luego, usando otra función (que podríamos crear
    # para obtener el usuario de la DB a partir del token), tendríamos el objeto 'User'.
    # Por ahora, simplemente decodificamos el token para obtener el email.
    token_data = decode_access_token(current_user) # 'current_user' aquí es el token puro del header.
                                                   # Lo decodificamos para obtener los datos.
    if token_data.get("sub") is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_email = token_data["sub"]

    # Aquí podríamos buscar el usuario completo en la DB si necesitáramos más detalles.
    user_from_db_query = await db.execute(text(f"SELECT id, email, is_active FROM users WHERE email = '{user_email}'"))
    user_from_db = user_from_db_query.scalar_one_or_none()

    if not user_from_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado en la base de datos"
        )
    
    # Retornamos solo los datos seguros del usuario.
    return {"user_email": user_from_db.email, "id": user_from_db.id, "is_active": user_from_db.is_active}


# --- Endpoint de prueba (ya existente) ---
@app.get("/")
async def read_root(db: AsyncSession = Depends(get_db)):
    """
    Endpoint de prueba para verificar que la API y la conexión a la base de datos están funcionando.
    Intenta obtener la versión de la base de datos para confirmar la conexión.
    """
    try:
        result = await db.execute(text("SELECT version();"))
        db_version = result.scalar_one()
        return {"message": f"¡Bienvenido a ConexAPI! El middleware está funcionando. DB Version: {db_version}"}
    except Exception as e:
        print(f"Error al conectar a la base de datos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al conectar a la base de datos: {e}"
        )


# Símbolos especiales explicados:
# `response_model=Token`: Decorador de FastAPI que asegura que la respuesta HTTP se formateará
#                         según el esquema Pydantic `Token`.
# `user: UserCreate`: Anotación de tipo que indica que el cuerpo de la petición HTTP
#                      debe corresponder al esquema Pydantic `UserCreate`. FastAPI lo valida automáticamente.
# `db.add(db_user)`: Añade un objeto de modelo (nuestro usuario) a la sesión de la base de datos,
#                    preparándolo para ser guardado.
# `await db.commit()`: Guarda los cambios pendientes en la base de datos de forma asíncrona.
# `await db.refresh(db_user)`: Vuelve a cargar el objeto `db_user` desde la base de datos después de un `commit`,
#                             para obtener valores generados por la DB (como el ID).
# `form_data: OAuth2PasswordRequestForm = Depends(...)`: Aquí, `OAuth2PasswordRequestForm` es una clase especial
#                                                        de FastAPI que espera un "username" y "password" en el cuerpo
#                                                        de la petición, como se usa típicamente para logins.
# `current_user: User = Depends(oauth2_scheme)`: Esta es la clave para proteger una ruta.
#                                                 `oauth2_scheme` (definido en `app.auth`) intenta leer el token
#                                                 del encabezado `Authorization: Bearer <token>`.
#                                                 Si el token es válido, FastAPI lo inyecta como `current_user`.
#                                                 Si no hay token, o es inválido, levanta una `HTTPException`.