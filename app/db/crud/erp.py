# ┌─────────────────────────────────────────────────────────────────────────────┐
# │ 📁 Ubicación: conexapi_backend/app/db/crud/erp.py                           │
# │ 📄 Archivo: erp.py                                                          │
# └─────────────────────────────────────────────────────────────────────────────┘
# 🎯 Objetivo: Guardar o actualizar credenciales del ERP (Usuario API y Access Key)
# en la base de datos. A futuro se añadirá encriptación AES256.
# 📌 Estado: CRUD funcional inicial sin cifrado (MVP Sprint 1).

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models.erp import ErpConfig
from app.schemas.erp import ErpConfigCreate

async def create_or_update_erp_config(
    db: AsyncSession, config_data: ErpConfigCreate
) -> ErpConfig:
    query = select(ErpConfig).where(ErpConfig.name == "siigo")
    result = await db.execute(query)
    existing = result.scalar_one_or_none()

    if existing:
        existing.usuario_api = config_data.usuario_api # type: ignore
        existing.access_key = config_data.access_key # type: ignore
        return existing  # Cambios se aplican al hacer commit en endpoint
    else:
        new_config = ErpConfig(
            name="siigo",
            usuario_api=config_data.usuario_api,
            access_key=config_data.access_key
        )
        db.add(new_config)
        return new_config
