# 📁 Ubicación: conexapi_backend/app/db/migrations/env.py

import os
import sys
from logging.config import fileConfig
from sqlalchemy import create_engine, pool
from alembic import context
from app.core.config import settings
from app.db.base import Base
from app.db.models.erp import ErpConfig
from dotenv import load_dotenv

# Carga variables de entorno
load_dotenv()

# Agrega la raíz al path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

# Alembic config
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata para autogenerar migraciones
target_metadata = Base.metadata

# Configura URL sin certificados
config.set_main_option(
    "sqlalchemy.url",
    f"mysql+pymysql://{settings.db_user}:{settings.db_password}@"
    f"{settings.db_host}:{settings.db_port}/{settings.db_name}"
)

def run_migrations_offline():
    """Modo offline: genera SQL sin conectarse."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Modo online: aplica migraciones directamente."""
    connectable = create_engine(
        config.get_main_option("sqlalchemy.url"), # type: ignore
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()

# Decide modo
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
