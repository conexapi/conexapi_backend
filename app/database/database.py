# Ubicación: /conexapi/conexapi_backend/app/database/database.py
# Propósito: Configura la conexión a la base de datos PostgreSQL utilizando SQLAlchemy.
#            Proporciona una función para obtener una sesión de base de datos.
# Dependencias: sqlalchemy, sqlalchemy.orm.sessionmaker, app.config, app.database.models

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.config import settings
from app.database.models import Base # <-- ¡NUEVA LÍNEA! Importa Base

engine = create_engine(
    settings.DATABASE_URL,
    echo=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ----- ¡AÑADE O MUEVE ESTA FUNCIÓN AQUÍ! -----
'''
def create_db_and_tables():
    # Propósito: Crea todas las tablas en la base de datos que están definidas por los modelos de SQLAlchemy.
    #            Esto se hace una vez al inicio de la aplicación si las tablas no existen.
    # Dependencias: app.database.models.Base
    print("Intentando crear tablas de base de datos...")
    Base.metadata.create_all(engine)
    print("Tablas de la base de datos creadas o actualizadas exitosamente.")
    '''
# ---------------------------------------------