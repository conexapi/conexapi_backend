# Ubicación: /conexapi/conexapi_backend/app/schemas/integration.py

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

class IntegrationConfigBase(BaseModel):
    platform_name: str = Field(..., min_length=1, max_length=50)
    api_key_or_username: str = Field(..., min_length=1)
    access_key_or_secret: str = Field(..., min_length=1)

    ml_access_token: Optional[str] = None
    ml_refresh_token: Optional[str] = None
    ml_token_expires_at: Optional[datetime] = None

    is_active: bool = True

class IntegrationConfigCreate(IntegrationConfigBase):
    pass

class IntegrationConfigUpdate(BaseModel):
    platform_name: Optional[str] = None
    api_key_or_username: Optional[str] = None
    access_key_or_secret: Optional[str] = None
    ml_access_token: Optional[str] = None
    ml_refresh_token: Optional[str] = None
    ml_token_expires_at: Optional[datetime] = None
    is_active: Optional[bool] = None

class IntegrationConfigInDB(IntegrationConfigBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True