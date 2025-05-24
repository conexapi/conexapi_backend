# Ubicación: /conexapi/conexapi_backend/app/config.py
# Propósito: Define cómo la aplicación carga y accede a las variables de entorno,
#            como la cadena de conexión a la base de datos y la clave secreta de JWT.
# Dependencias: pydantic-settings

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Propósito: Clase que define la estructura de nuestras variables de entorno.
    #            BaseSettings de Pydantic Settings lee automáticamente del .env.
    #            Estas variables son cruciales para la configuración de la aplicación.

    database_url: str
    # database_url (str): Cadena de conexión a la base de datos.

    secret_key: str  # <-- ¡NUEVA LÍNEA!
    # secret_key (str): Clave secreta utilizada para firmar los tokens JWT.
    #                   Debe ser una cadena de texto larga y aleatoria.

    algorithm: str = "HS256" # <-- ¡NUEVA LÍNEA!
    # algorithm (str): Algoritmo de cifrado para los tokens JWT (por defecto HS256).

    access_token_expire_minutes: int = 30 # <-- ¡NUEVA LÍNEA!
    # access_token_expire_minutes (int): Tiempo de expiración del token de acceso en minutos.

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

settings = Settings()