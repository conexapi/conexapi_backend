# Guardar como: /conexapi/conexapi_backend/create_siigo_config.py

from sqlalchemy.orm import Session
# MODIFICACIÓN CLAVE AQUÍ: Importar get_db directamente desde app.database.database
from app.database.database import get_db, SessionLocal, Base, engine 
from app.database import models # Tu modelo IntegrationConfig
from app.schemas import integration as schemas_integration # Necesitas IntegrationConfigCreate para crear
from app.crud import integration as crud_integration
from datetime import datetime, timezone

def create_siigo_config_entry():
    db: Session = next(get_db()) # Obtiene una sesión de base de datos
    try:
        # Primero, asegúrate de que la tabla exista (si no la creas al iniciar FastAPI)
        # Esto es solo para un script standalone de una sola vez
        # Base.metadata.create_all(bind=engine) 

        # Verificar si ya existe una configuración para "SIIGO"
        existing_config = db.query(models.IntegrationConfig).filter(models.IntegrationConfig.platform_name == "SIIGO").first()
        if existing_config:
            print(f"La configuración para 'SIIGO' ya existe (ID: {existing_config.id}). No se creará una nueva entrada.")
            print("Si necesitas actualizarla, usa un script de actualización o tu API de administración.")
            return

        # Definir los datos para la nueva configuración de Siigo
        siigo_config_data = schemas_integration.IntegrationConfigCreate(
            platform_name="SIIGO",
            api_key_or_username="sandbox@siigoapi.com",
            access_key_or_secret="NDllMzI0NmEtNjExZC00NGM3LWE3OTQtMWUyNTNlZWU0ZTM0OkosU2MwLD4xQ08=",
            # Los campos nullable=True no son obligatorios al crear si no tienen valor
            # ml_access_token=None,
            # ml_refresh_token=None,
            # ml_token_expires_at=None,
            is_active=True # Activamos la integración por defecto
        )

        # Usar la función CRUD para crear la nueva configuración
        # Asumimos que crud_integration.create_integration_config está disponible
        new_config = crud_integration.create_integration_config(db, config=siigo_config_data)

        if new_config:
            print("¡Configuración de 'SIIGO' creada exitosamente en la base de datos!")
            print(f"ID: {new_config.id}")
            print(f"Platform: {new_config.platform_name}")
            print(f"Username (Mock): {new_config.api_key_or_username}")
            print(f"Access Key (Mock): {new_config.access_key_or_secret}")
        else:
            print("Fallo al crear la configuración de 'SIIGO'.")
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")
        db.rollback() # Si algo falla, revierte los cambios
    finally:
        db.close() # Asegúrate de cerrar la sesión de la base de datos

if __name__ == "__main__":
    print("Intentando crear la configuración de 'SIIGO' en la base de datos...")
    create_siigo_config_entry()