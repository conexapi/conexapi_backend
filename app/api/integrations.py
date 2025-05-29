# Ubicación: /conexapi/conexapi_backend/app/api/integrations.py
# Propósito: Define los endpoints de la API para gestionar las configuraciones de integración
#            con sistemas externos (ej. SIIGO, MercadoLibre).
# Dependencias: fastapi, sqlalchemy.orm.Session, app.database.database, app.crud.integration,
#               app.schemas.integration, app.utils.auth

from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Path # Asegúrate de que Path esté aquí si lo usas
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.crud import integration as crud_integration
from app.schemas import integration as schemas_integration
from app.schemas import user as schemas_user
from app.utils.auth import is_admin
from app.database import models # Esta importación está bien si la necesitas en otras partes.
from app.services import siigo as siigo_service

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
    current_admin_user: Annotated[schemas_user.UserInDB, Depends(is_admin())],
    db: Session = Depends(get_db),
    skip: int = 0, limit: int = 100
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
    # ¡CÓDIGO DESCOMENTADO Y CORREGIDO AQUÍ ABAJO!
    db_config = crud_integration.get_integration_config(db, config_id=config_id)
    if db_config is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Configuración no encontrada")

    # Si hay un cambio de nombre de plataforma, verificar que no haya duplicados
    if config_update.platform_name and config_update.platform_name != db_config.platform_name:
        existing_config_by_name = crud_integration.get_integration_config_by_platform_name(db, platform_name=config_update.platform_name)
        if existing_config_by_name is not None:
            if config_id != existing_config_by_name.id: # Asegurarse de que no sea la misma configuración
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Ya existe una configuración para la plataforma '{config_update.platform_name}'."
                )

    # Llamada corregida a la función CRUD
    updated_config = crud_integration.update_integration_config(db=db, config_id=config_id, config_update_data=config_update) # <-- ¡CORRECCIÓN AQUÍ!
    if updated_config is None:
           raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Configuración no encontrada después de la actualización (posible error interno)")
    return updated_config


async def activate_integration_config(
    config_id: int,
    current_admin_user: Annotated[schemas_user.UserInDB, Depends(is_admin())],
    db: Session = Depends(get_db)
):
    db_config = crud_integration.get_integration_config(db, config_id)
    if not db_config:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Configuración no encontrada")

    # Actualizar is_active a True si no lo está
    if db_config.is_active is False:
        update_data = schemas_integration.IntegrationConfigUpdate(is_active=True)
        db_config = crud_integration.update_integration_config(db, config_id, update_data)
        if not db_config: # Re-chequear por si falla la actualización
             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="No se pudo actualizar el estado de la configuración.")

    # Si es una integración de SIIGO, intentamos obtener el token
    if db_config.platform_name.upper() == "SIIGO":
        print(f"Intentando obtener token de SIIGO para configuración {config_id}...")
        updated_config = siigo_service.get_siigo_token(db, db_config)
        if not updated_config:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No se pudo obtener el token de SIIGO. Verifica las credenciales de la aplicación y del cliente."
            )
        print(f"Token de SIIGO obtenido y guardado para configuración {config_id}.")
        return updated_config
    # Puedes añadir más lógicas para otras plataformas aquí (ej. Mercado Libre)
    elif db_config.platform_name.upper() == "MERCADOLIBRE":
        # Por ahora, solo confirmamos activación, el flujo de ML requiere redirección OAuth
        # Esta parte se desarrollará después del SIIGO
        print(f"La configuración de MercadoLibre {config_id} ha sido activada. El flujo OAuth se manejará por separado.")
        return db_config # Retornar la config actualizada

    # Si la plataforma no es SIIGO ni ML, simplemente confirmamos que se activó
    return db_config


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