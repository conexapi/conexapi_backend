# Ubicación: /conexapi/conexapi_backend/app/database/database.py
# Propósito: Configura la conexión a la base de datos y provee una sesión para interactuar con ella.
#            También contiene la función para crear todas las tablas definidas en models.py.
# Dependencias: sqlalchemy, config, models

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager

from app.config import settings
from app.database.models import Base

# Símbolo especial: create_engine() es una función de SQLAlchemy que crea un "motor" de base de datos.
#                   Este motor es como la maquinaria que se encarga de hablar con tu base de datos real.
#                   El 'echo=True' mostrará las sentencias SQL que se ejecutan (útil para depurar).
engine = create_engine(settings.database_url, echo=True)

# Símbolo especial: sessionmaker crea una clase de "sesión". Una sesión es como un área de trabajo
#                   donde puedes preparar tus operaciones de base de datos antes de enviarlas.
#                   autocommit=False significa que los cambios no se guardan automáticamente.
#                   autoflush=False significa que los cambios no se envían a la DB hasta que se guarda o se hace commit.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_db_and_tables():
    # Propósito: Crea todas las tablas en la base de datos que están definidas en models.py.
    #            Esto es crucial la primera vez que configuras la DB.
    # Símbolo especial: Base.metadata.create_all(engine) le dice al motor de la DB que
    #                   cree todas las tablas que 'Base' conoce (todas las clases que heredan de Base).
    try:
        Base.metadata.create_all(bind=engine)
        print("Tablas de la base de datos creadas o actualizadas exitosamente.")
    except SQLAlchemyError as e:
        print(f"Error al crear las tablas de la base de datos: {e}")
        # >>: El operador ">>" no es un operador Python estándar, pero se usa aquí como
        #    un marcador para indicar una salida esperada o un mensaje.

@contextmanager
def get_db():
    # Propósito: Proporciona una sesión de base de datos que se cierra automáticamente.
    #            Es un "context manager" que asegura que la conexión a la DB se maneje correctamente.
    #            Es como abrir un libro para leer y asegurarte de cerrarlo al terminar.
    # Símbolo especial: 'yield' en un generador/context manager. Permite que la función
    #                   devuelva un valor (la sesión de DB) y luego reanude la ejecución
    #                   cuando el bloque 'with' termina, para asegurar que la sesión se cierre.
    db = SessionLocal()
    try:
        yield db
        # ->: La flecha '->' se usa en Python para indicar el tipo de retorno esperado de una función.
        #     Aquí, indica que get_db() es un generador que produce un objeto de tipo Session.
    except SQLAlchemyError as e:
        db.rollback() # Si algo falla, deshace los cambios.
        print(f"Error en la transacción de la base de datos: {e}")
        raise # Vuelve a lanzar la excepción.
    finally:
        db.close() # Asegura que la sesión se cierre, liberando los recursos de la DB.