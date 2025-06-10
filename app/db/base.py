# ┌─────────────────────────────────────────────────────────────────────────────┐
# │ 📁 Ubicación: conexapi_backend/app/db/base.py                               │
# │ 📄 Archivo: base.py                                                         │
# └─────────────────────────────────────────────────────────────────────────────┘
# 🎯 Objetivo: Definir la clase base de modelos SQLAlchemy (declarative_base)
# utilizada por todos los modelos ORM del proyecto.
# 📌 Estado: Base inicial lista y funcional.

#Este archivo ya permite que todos tus modelos (como ErpConfig) hereden de una misma base y puedan ser reconocidos por el sistema de migraciones y sesión.

from sqlalchemy.orm import declarative_base

Base = declarative_base()
