# Ubicación: /conexapi/conexapi_backend/app/crud/integration.py
# Propósito: Contiene funciones para interactuar con la tabla 'integration_configs' en la base de datos.
#            Proporciona operaciones CRUD para las configuraciones de integración.
# Dependencias: sqlalchemy.orm.Session, app.database.models, app.schemas.integration

from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete
from typing import List, Optional, Sequence # <-- Asegúrate de estas importaciones

from app.database import models # <-- Importante: necesitamos acceso a los modelos de DB
from app.schemas import integration as schemas_integration

# --- Funciones CRUD para IntegrationConfig ---

def get_integration_config_by_platform_name(db: Session, platform_name: str) -> Optional[models.IntegrationConfig]:
    """
    Recupera una configuración de integración por su nombre de plataforma.
    """
    return db.scalar(
        select(models.IntegrationConfig).where(models.IntegrationConfig.platform_name == platform_name)
    )

def get_integration_config(db: Session, config_id: int) -> Optional[models.IntegrationConfig]:
    """
    Recupera una configuración de integración por su ID.
    """
    return db.scalar(
        select(models.IntegrationConfig).where(models.IntegrationConfig.id == config_id)
    )

def get_integration_configs(db: Session, skip: int = 0, limit: int = 100) -> Sequence[models.IntegrationConfig]: # <-- ¡Tipo de retorno cambiado a Sequence!
    """
    Recupera múltiples configuraciones de integración.
    """
    return db.scalars(select(models.IntegrationConfig).offset(skip).limit(limit)).all()

def create_integration_config(db: Session, config: schemas_integration.IntegrationConfigCreate) -> models.IntegrationConfig:
    """
    Crea una nueva configuración de integración en la base de datos.
    """
    db_config = models.IntegrationConfig(
        platform_name=config.platform_name,
        api_key_or_username=config.api_key_or_username,
        access_key_or_secret=config.access_key_or_secret,
        ml_access_token=config.ml_access_token,
        ml_refresh_token=config.ml_refresh_token,
        ml_token_expires_at=config.ml_token_expires_at,
        is_active=config.is_active
    )
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    return db_config

def update_integration_config(
    db: Session,
    config_id: int,
    # Puede recibir un IntegrationConfigUpdate o IntegrationConfigTokenUpdate
    config_update_data: schemas_integration.IntegrationConfigUpdate | schemas_integration.IntegrationConfigTokenUpdate
) -> Optional[models.IntegrationConfig]:
    db_config = get_integration_config(db, config_id)
    if db_config:
        # model_dump(exclude_unset=True) solo incluye campos que se hayan proporcionado en la actualización.
        # Usar model_dump para obtener solo los campos seteados en el Pydantic Schema
        update_data = config_update_data.model_dump(exclude_unset=True)
        if update_data:
             # Crea la sentencia UPDATE para la configuración específica por ID.
            stmt = update(models.IntegrationConfig).where(models.IntegrationConfig.id == config_id).values(**update_data)
            db.execute(stmt)
            db.commit()
            db.refresh(db_config)# Refrescar la instancia para tener los últimos datos
    return db_config


def delete_integration_config(db: Session, config_id: int) -> Optional[models.IntegrationConfig]:
    """
    Elimina una configuración de integración de la base de datos.
    """
    db_config = get_integration_config(db, config_id)
    if db_config:
        stmt = delete(models.IntegrationConfig).where(models.IntegrationConfig.id == config_id)
        db.execute(stmt)
        db.commit()
    return db_config # Retorna el objeto eliminado o None si no se encontró