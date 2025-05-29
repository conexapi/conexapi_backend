from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Esto es crucial: importa tus modelos y la Base de tu aplicación
import sys
import os
sys.path.append(os.path.abspath(".")) # Asegura que el path de la aplicación sea accesible
from app.database.models import Base  # Importa la Base de tus modelos
from app.config import settings     # Importa tu configuración para la DATABASE_URL


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
#target_metadata = None
target_metadata = Base.metadata # ¡MUY IMPORTANTE! Aquí conectamos tus modelos a Alembic

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

     url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    '''
    '''
    ============================================================
    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    beause it will associate the context with a connection
    URL.

    For production environments, this is the preferred
    method when there is no active database connection.

    """
   # Ya no necesitamos configurar 'sqlalchemy.url' en alembic.ini.
    # En su lugar, lo obtenemos de nuestra configuración.
    url = settings.DATABASE_URL # ¡Obtenemos la URL de tu configuración!
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

     connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

    """
   
    # Aquí también obtenemos la URL de la configuración
    configuration = config.get_section(config.config_ini_section, {})
    configuration['sqlalchemy.url'] = settings.DATABASE_URL # ¡Configuramos la URL aquí!

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # Para evitar problemas con la autogeneración de cambios en el esquema si no se tiene una DB limpia
            compare_type=True
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
