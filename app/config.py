# Ubicación: /conexapi/conexapi_backend/app/config.py
# Propósito: Define cómo la aplicación carga y accede a las variables de entorno,
#            como la cadena de conexión a la base de datos.
# Dependencias: pydantic-settings

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Propósito: Clase que define la estructura de nuestras variables de entorno.
    #            BaseSettings de Pydantic Settings lee automáticamente del .env.
    #            Estas variables son cruciales para la configuración de la aplicación.

    database_url: str
    # database_url (str): Aquí se almacenará la cadena de conexión a la base de datos.
    #                     Pydantic Settings la leerá de la variable de entorno DATABASE_URL.

    model_config = SettingsConfigDict(
        env_file=".env",       # Símbolo especial: env_file indica a Pydantic que lea de .env
        extra="ignore"         # extra="ignore" ignora variables en .env que no estén definidas aquí.
    )

# Símbolo especial: La instancia de la clase Settings se crea para ser importada
#                   y usada en otras partes de la aplicación.
settings = Settings()