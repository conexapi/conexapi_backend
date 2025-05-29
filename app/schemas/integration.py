# Ubicación: /conexapi/conexapi_backend/app/schemas/integration.py
# Propósito: Define la estructura (esquemas) de los datos para las configuraciones de integración.
# Dependencias: pydantic, datetime


from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class IntegrationConfigBase(BaseModel):
    platform_name: str = Field(..., min_length=1, max_length=50)
    api_key_or_username: str = Field(..., min_length=1)
    access_key_or_secret: str = Field(..., min_length=1)

    ml_access_token: Optional[str] = None
    ml_refresh_token: Optional[str] = None
    ml_token_expires_at: Optional[datetime] = None

    refresh_interval_minutes: int = Field(default=1430, ge=1) # Mínimo 1 minuto

    is_active: bool = True

class IntegrationConfigCreate(IntegrationConfigBase):
    pass

# ... tus esquemas IntegrationConfigCreate, IntegrationConfigUpdate, IntegrationConfigInDB ...
# --- ¡NUEVO ESQUEMA PARA LA ACTUALIZACIÓN DE TOKENS! ---
class IntegrationConfigTokenUpdate(BaseModel):
    ml_access_token: Optional[str] = None
    ml_refresh_token: Optional[str] = None
    ml_token_expires_at: Optional[datetime] = None
    refresh_interval_minutes: Optional[int] = Field(default=None, ge=1) # También opcional para actualización de token
    # Puedes añadir aquí también los tokens de Siigo si los manejas de forma similar


# --------------------------------------------------------

class IntegrationConfigUpdate(BaseModel):
    platform_name: Optional[str] = None
    api_key_or_username: Optional[str] = None
    access_key_or_secret: Optional[str] = None
    ml_access_token: Optional[str] = None
    ml_refresh_token: Optional[str] = None
    ml_token_expires_at: Optional[datetime] = None
    refresh_interval_minutes: Optional[int] = Field(default=None, ge=1)
    is_active: Optional[bool] = None

# Esquema para representar la configuración tal como se lee desde la base de datos (con ID y fechas).
class IntegrationConfigInDB(IntegrationConfigBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        extra="ignore" # Permite campos adicionales para flexibilidad