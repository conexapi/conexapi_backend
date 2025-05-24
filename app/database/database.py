# Ubicación: /conexapi/conexapi_backend/app/database/database.py
# Propósito: Configura la conexión a la base de datos PostgreSQL utilizando SQLAlchemy.
#            Proporciona una función para obtener una sesión de base de datos.
# Dependencias: sqlalchemy, sqlalchemy.orm.sessionmaker, app.config

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session # Importar Session directamente
from app.config import settings

# Propósito: Crea el motor de la base de datos.
#            SQLALCHEMY_DATABASE_URL es la cadena de conexión que cargamos de las variables de entorno.
#            echo=True: hará que SQLAlchemy imprima todas las sentencias SQL que ejecuta,
#                       lo cual es útil para depuración en desarrollo.
engine = create_engine(
    settings.database_url,
    echo=True # Mostrar las consultas SQL en la consola.
)

# Propósito: Configura una clase SessionLocal para crear sesiones de base de datos.
#            autocommit=False: Los cambios no se guardan automáticamente, necesitas llamar a db.commit().
#            autoflush=False: Los objetos no se vacían automáticamente a la DB antes de cada consulta.
#            bind=engine: Asocia esta clase de sesión con nuestro motor de base de datos.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    # Propósito: Proporciona una sesión de base de datos que se cierra automáticamente.
    #            Esto es lo que FastAPI usará con Depends().
    # Símbolo especial: yield. Hace que esta función sea un "generador de contexto".
    #                   La parte antes de 'yield' se ejecuta al inicio (abre la sesión).
    #                   La parte después de 'yield' se ejecuta al final (cierra la sesión).
    db = SessionLocal() # Crea una nueva sesión de la base de datos.
    # Símbolo especial: try...finally. Asegura que la sesión se cierre incluso si hay errores.
    try:
        yield db # Devuelve la sesión de la base de datos al código que la solicitó.
    finally:
        db.close() # Cierra la sesión de la base de datos después de usarla.