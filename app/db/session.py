# ┌─────────────────────────────────────────────────────────────────────────────┐
# │ 📁 Ubicación: conexapi_backend/app/db/session.py                            │
# │ 📄 Archivo: session.py                                                      │
# └─────────────────────────────────────────────────────────────────────────────┘
# 🎯 Objetivo: Configurar la conexión asincrónica a MySQL usando SQLAlchemy
# y aiomysql. Exporta el motor y el generador de sesiones para FastAPI.
# 📌 Estado: Conexión funcional en entorno local/producción (vía variables .env)

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from typing import AsyncGenerator
from typing import cast

DATABASE_URL = (
    f"mysql+aiomysql://{settings.db_user}:{settings.db_password}@"
    f"{settings.db_host}:{settings.db_port}/{settings.db_name}"
)

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)  # type: ignore

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    session = cast(AsyncSession, AsyncSessionLocal())
    async with session:
        yield session