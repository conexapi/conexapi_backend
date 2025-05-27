# Ubicación: /conexapi/conexapi_backend/app/schemas/integration.py

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

class IntegrationConfigBase(BaseModel):
    # Nombre de la plataforma (ej. "SIIGO", "MERCADOLIBRE")
    platform_name: str = Field(..., min_length=1, max_length=50) # ... significa que es obligatorio

    # Credenciales para Siigo: api_key_or_username = Usuario API, access_key_or_secret = Access Key
    # Para ML (nuestras credenciales de aplicación): api_key_or_username = Client ID, access_key_or_secret = Client Secret
    api_key_or_username: str = Field(..., min_length=1)
    access_key_or_secret: str = Field(..., min_length=1)

    # Campos específicos para MercadoLibre OAuth tokens (gestionados por el sistema, no por el usuario directamente al crear/actualizar config)
    # Estos se llenarán después del flujo de autorización de ML
    ml_access_token: Optional[str] = None
    ml_refresh_token: Optional[str] = None
    ml_token_expires_at: Optional[datetime] = None

    is_active: bool = True # Para habilitar/deshabilitar la integración

class IntegrationConfigCreate(IntegrationConfigBase):
    # No hay campos adicionales específicos para la creación por ahora.
    pass

class IntegrationConfigUpdate(BaseModel):
    # Todos los campos son opcionales para actualizaciones parciales
    platform_name: Optional[str] = None
    api_key_or_username: Optional[str] = None
    access_key_or_secret: Optional[str] = None
    ml_access_token: Optional[str] = None
    ml_refresh_token: Optional[str] = None
    ml_token_expires_at: Optional[datetime] = None
    is_active: Optional[bool] = None

class IntegrationConfigInDB(IntegrationConfigBase):
    # Esquema para representar la configuración tal como se lee desde la base de datos (con ID y fechas)
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True