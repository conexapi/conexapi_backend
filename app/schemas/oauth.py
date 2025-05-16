# app/schemas/oauth.py

#from pydantic import BaseModel, Field
from pydantic import BaseModel, Field
from pydantic.config import ConfigDict
from typing import Optional
from datetime import datetime

#FastAPI usa los modelos Pydantic para asegurar que los datos entrantes (de formularios, JSON, etc.) cumplan con una estructura específica antes de ser procesados o guardados en la base de datos.
#Esto protege tu app contra:
#Datos faltantes
#Tipos incorrectos
#Errores de usuario o de integraciones externas
#Además, estructura los datos de salida (por ejemplo, cuando haces un GET) para que tengan una forma clara y predecible.

class OAuthTokenBase(BaseModel):
    user_id: int
    platform: str
    access_token: str
    token_type: Optional[str] = None
    expires_in: Optional[int] = None
    scope: Optional[str] = None
    refresh_token: Optional[str] = None
    expires_at: Optional[datetime] = None

class OAuthTokenCreate(OAuthTokenBase):
    expires_at: Optional[datetime] = None
    pass

class OAuthTokenUpdate(BaseModel):
    access_token: Optional[str]
    token_type: Optional[str]
    expires_in: Optional[int]
    scope: Optional[str]
    refresh_token: Optional[str]
    updated_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None

class OAuthTokenOut(OAuthTokenBase):
    id: int
    created_at: datetime
    updated_at: datetime
    expires_at: Optional[datetime] = None

    model_config: ConfigDict = {'from_attributes': True}

    #model_config = {from_attributes=True}

    #class Config:
    #    orm_mode = True

#Crear el modelo Pydantic para oauth_tokens
#Esto nos servirá para validar los datos que vienen del flujo OAuth2 de MercadoLibre #antes de guardarlos en la base de datos. También permitirá mantener la coherencia si en #el futuro agregamos validaciones adicionales o usamos esos datos en respuestas de la API.
# Estructura esperada del modelo (OAuthToken)
#Basado en la tabla oauth_tokens, el modelo sería algo como esto:

class OAuthToken(BaseModel):
    user_id: int
    platform: str = Field(default="mercadolibre")
    access_token: str
    token_type: Optional[str] = None
    expires_in: Optional[int] = None
    scope: Optional[str] = None
    refresh_token: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None