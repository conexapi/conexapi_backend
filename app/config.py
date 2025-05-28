# Ubicación: /conexapi/conexapi_backend/app/config.py
# Propósito: Define cómo la aplicación carga y accede a las variables de entorno,
#            como la cadena de conexión a la base de datos y la clave secreta de JWT.
# Dependencias: pydantic-settings

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    # Propósito: Clase que define la estructura de nuestras variables de entorno.
    #            BaseSettings de Pydantic Settings lee automáticamente del .env.
    #            Estas variables son cruciales para la configuración de la aplicación.

    database_url: str
    # database_url (str): Cadena de conexión a la base de datos.

    SECRET_KEY: str  # <-- ¡NUEVA LÍNEA!
    # secret_key (str): Clave secreta utilizada para firmar los tokens JWT.
    #                   Debe ser una cadena de texto larga y aleatoria.

    ALGORITHM: str  # <-- ¡NUEVA LÍNEA!
    # algorithm (str): Algoritmo de cifrado para los tokens JWT (por defecto HS256).

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30 # <-- ¡NUEVA LÍNEA!
    # access_token_expire_minutes (int): Tiempo de expiración del token de acceso en minutos.

    # --- ¡NUEVAS VARIABLES PARA MARKETPLACES! ---
    MERCADOLIBRE_APP_ID: str
    MERCADOLIBRE_SECRET_KEY: str

     # --- ¡NUEVAS VARIABLES PARA ERPs! ---
    SIIGO_CLIENT_ID: str # Si lo usas más adelante
    SIIGO_CLIENT_SECRET: str # Si lo usas más adelante
    # --------------------------------------------


    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

settings = Settings()