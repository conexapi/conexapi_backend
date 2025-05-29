# Ubicación: /conexapi/conexapi_backend/app/config.py
# Propósito: Define cómo la aplicación carga y accede a las variables de entorno,
#            como la cadena de conexión a la base de datos y la clave secreta de JWT.
# Dependencias: pydantic-settings

from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    # Propósito: Clase que define la estructura de nuestras variables de entorno.
    #            BaseSettings de Pydantic Settings lee automáticamente del .env.
    #            Estas variables son cruciales para la configuración de la aplicación.

    DATABASE_URL: str
    # database_url (str): Cadena de conexión a la base de datos.

    SECRET_KEY: str 
    # secret_key (str): Clave secreta utilizada para firmar los tokens JWT.
    #                   Debe ser una cadena de texto larga y aleatoria.

    ALGORITHM: str 
    # algorithm (str): Algoritmo de cifrado para los tokens JWT (por defecto HS256).

    ACCESS_TOKEN_EXPIRE_MINUTES: int =30
    # access_token_expire_minutes (int): Tiempo de expiración del token de acceso en minutos.

    # --- VARIABLES PARA MARKETPLACES ---
    MERCADOLIBRE_APP_ID: str
    MERCADOLIBRE_SECRET_KEY: str
    MERCADOLIBRE_AUTH_URL: str ="https://auth.mercadolibre.com/oauth/token"
    MERCADOLIBRE_API_BASE_URL: str = "https://api.mercadolibre.com"
    MERCADOLIBRE_REDIRECT_URI: str = "http://localhost:8000/integrations/configs/mercadolibre/callback" 
    #"https://api.conexapi.com/ml/auth/callback"


     # ---VARIABLES PARA ERPs! ---
    SIIGO_CLIENT_ID: str 
    SIIGO_CLIENT_SECRET: str 
    SIIGO_PARTNER_ID: str
    SIIGO_AUTH_URL:str
    #=  "https://siigoapi.postman.co/auth" # 

    # URL del mock de Siigo o sandbox real
    SIIGO_API_BASE_URL:str =  "https://siigoapi.postman.co/V1" # URL del mock de Siigo o sandbox real

    # --------------------------------------------


    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )
# Instanciamos la configuración para que pueda ser importada y usada en toda la aplicación.
settings = Settings()