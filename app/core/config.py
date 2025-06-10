# ┌─────────────────────────────────────────────────────────────────────────────┐
# │ 📁 Ubicación: conexapi_backend/app/core/config.py                           │
# │ 📄 Archivo: config.py                                                       │
# └─────────────────────────────────────────────────────────────────────────────┘
# 🎯 Objetivo: Cargar y exponer las variables de entorno necesarias para
# la configuración del sistema (MySQL, SIIGO, etc.) usando pydantic-settings.
# 📌 Estado: Actualizado con campos SSL opcionales.

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    db_host: str
    db_port: int = 3306
    db_user: str
    db_password: str
    db_name: str
    
    # Campos SSL opcionales (vacíos por defecto)
    db_ssl_ca: str = ""
    db_ssl_cert: str = ""
    db_ssl_key: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"  # ✅ ¡Esto evita el ValidationError por campos no definidos!

settings = Settings()# type: ignore