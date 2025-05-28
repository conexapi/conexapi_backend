# Ubicación: /conexapi/conexapi_backend/app/api/integrations.py
# Propósito: Define los endpoints de la API para gestionar las configuraciones de integración
#            con sistemas externos (ej. SIIGO, MercadoLibre).
# Dependencias: fastapi, sqlalchemy.orm.Session, app.database.database, app.crud.integration,
#               app.schemas.integration, app.utils.auth

from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.crud import integration as crud_integration
from app.schemas import integration as schemas_integration
from app.schemas import user as schemas_user
from app.utils.auth import is_admin
from app.database import models

router = APIRouter(
    prefix="/integrations",
    tags=["Integrations"]
)

# Endpoint para crear una nueva configuración de integración
@router.post(
    "/configs/",
    response_model=schemas_integration.IntegrationConfigInDB,
    status_code=status.HTTP_201_CREATED,
    summary="Crea una nueva configuración de integración (solo administradores)",
    response_description="Configuración de integración creada exitosamente."
)
async def create_integration_config(
    config: schemas_integration.IntegrationConfigCreate,
    current_admin_user: Annotated[schemas_user.UserInDB, Depends(is_admin())],
    db: Session = Depends(get_db)
):
    db_config = crud_integration.get_integration_config_by_platform_name(db, platform_name=config.platform_name)
    if db_config:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe una configuración para la plataforma '{config.platform_name}'."
        )
    return crud_integration.create_integration_config(db=db, config=config)

# Endpoint para obtener todas las configuraciones de integración
@router.get(
    "/configs/",
    response_model=List[schemas_integration.IntegrationConfigInDB],
    summary="Obtiene todas las configuraciones de integración (solo administradores)",
    response_description="Lista de configuraciones de integración."
)
async def read_integration_configs(
    # ¡ORDEN DE ARGUMENTOS FINALMENTE AJUSTADO PARA PYLANCE!
    current_admin_user: Annotated[schemas_user.UserInDB, Depends(is_admin())],
    db: Session = Depends(get_db),
    skip: int = 0, limit: int = 100 # Los argumentos con valor por defecto van al final
):
    configs = crud_integration.get_integration_configs(db, skip=skip, limit=limit)
    return configs

# Endpoint para obtener una configuración de integración por ID
@router.get(
    "/configs/{config_id}",
    response_model=schemas_integration.IntegrationConfigInDB,
    summary="Obtiene una configuración de integración por ID (solo administradores)",
    response_description="Configuración de integración encontrada."
)
async def read_integration_config(
    config_id: int,
    current_admin_user: Annotated[schemas_user.UserInDB, Depends(is_admin())],
    db: Session = Depends(get_db)
):
    db_config = crud_integration.get_integration_config(db, config_id=config_id)
    if db_config is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Configuración no encontrada")
    return db_config

# Endpoint para actualizar una configuración de integración
@router.patch(
    "/configs/{config_id}",
    response_model=schemas_integration.IntegrationConfigInDB,
    summary="Actualiza una configuración de integración (solo administradores)",
    response_description="Configuración de integración actualizada exitosamente."
)
async def update_integration_config(
    config_id: int,
    config_update: schemas_integration.IntegrationConfigUpdate,
    current_admin_user: Annotated[schemas_user.UserInDB, Depends(is_admin())],
    db: Session = Depends(get_db)
):
    db_config = crud_integration.get_integration_config(db, config_id=config_id)
    if db_config is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Configuración no encontrada")

    if config_update.platform_name and config_update.platform_name != db_config.platform_name:
        existing_config_by_name = crud_integration.get_integration_config_by_platform_name(db, platform_name=config_update.platform_name)

        if existing_config_by_name is not None:
            if config_id != existing_config_by_name.id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Ya existe una configuración para la plataforma '{config_update.platform_name}'."
                )

    updated_config = crud_integration.update_integration_config(db=db, config_id=config_id, config_update=config_update)
    if updated_config is None:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Configuración no encontrada después de la actualización (posible error interno)")
    return updated_config

# Endpoint para eliminar una configuración de integración
@router.delete(
    "/configs/{config_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Elimina una configuración de integración (solo administradores)",
    response_description="Configuración de integración eliminada exitosamente."
)
async def delete_integration_config(
    config_id: int,
    current_admin_user: Annotated[schemas_user.UserInDB, Depends(is_admin())],
    db: Session = Depends(get_db)
):
    db_config = crud_integration.delete_integration_config(db, config_id=config_id)
    if db_config is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Configuración no encontrada")
    return {"message": "Configuración eliminada exitosamente"}