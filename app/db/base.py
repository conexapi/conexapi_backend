# ┌──────────────────────────────────────────────────────────────────┐
# │ 📁 Ubicación: conexapi_backend/app/db/base.py                    │
# │ 📄 Archivo: base.py                                              │
# └──────────────────────────────────────────────────────────────────┘
# 🎯 Objetivo: Centralizar metadata y registros de modelos SQLAlchemy
# 📌 Estado: Versión corregida sin import circular.

from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

# ✅ Importa aquí todos los modelos que se deben registrar en Alembic
# Pero HAZ ESTO DESPUÉS de definir `Base` (y no dentro de los modelos)
from app.db.models import erp  # 👈 Esto ya es seguro
