# ┌─────────────────────────────────────────────────────────────────────────────┐
# │ 📁 Ubicación: conexapi_backend/app/db/migrations/env.py                     │
# │ 📄 Archivo: env.py                                                          │
# └─────────────────────────────────────────────────────────────────────────────┘
# 🎯 Objetivo: Configurar Alembic para ejecutar migraciones con base en los
# modelos definidos en SQLAlchemy. Usa configuración desde `.env`.
# 📌 Estado: Corregido para conexiones SSL requeridas.

import os
import sys
from logging.config import fileConfig
from sqlalchemy import create_engine, engine_from_config, pool
from alembic import context
from alembic.config import Config
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# 📌 Permite importar config/settings desde la raíz del proyecto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from app.db.base import Base

# 🔄 Carga las variables del .env antes de todo
load_dotenv()

class Settings(BaseSettings):
    db_user: str
    db_password: str
    db_host: str
    db_port: int
    db_name: str
    db_ssl_ca: str
    db_ssl_cert: str
    db_ssl_key: str

    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignora variables extra del .env

# ✅ Instancia una sola vez
try:
    settings = Settings()
except Exception as e:
    raise RuntimeError(f"Error cargando configuración del entorno: {e}")

# Alembic Config object
config: Config = context.config

# Configura logs si es necesario
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 🎯 Este es el metadata que Alembic usará para autogenerar migraciones
target_metadata = Base.metadata

def get_ssl_args():
    """Retorna los argumentos SSL para la conexión"""
    return {
        "ssl": {
            "ca": settings.db_ssl_ca,
            "cert": settings.db_ssl_cert,
            "key": settings.db_ssl_key
        }
    }

def get_database_url():
    """Retorna la URL de la base de datos con pymysql"""
    return (
        f"mysql+pymysql://{settings.db_user}:{settings.db_password}@"
        f"{settings.db_host}:{settings.db_port}/{settings.db_name}"
    )

def run_migrations_offline() -> None:
    """Ejecutar migraciones en modo 'offline'."""
    url = get_database_url()
    
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Ejecuta migraciones en modo 'online' usando conexión segura SSL."""
    try:
        # Creamos el engine con certificados SSL
        connectable = create_engine(
            get_database_url(),
            connect_args=get_ssl_args(),
            poolclass=pool.NullPool,
            future=True
        )

        with connectable.connect() as connection:
            context.configure(
                connection=connection,
                target_metadata=target_metadata
            )

            with context.begin_transaction():
                context.run_migrations()

    except Exception as e:
        print(f"Error detallado: {e}")
        raise RuntimeError(f"Error durante la ejecución de migraciones Alembic: {e}")

# Punto de entrada principal
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()