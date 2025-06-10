# ┌──────────────────────────────────────────────────────────────────────┐
# │ 📁 Ubicación: conexapi_backend/app/schemas/erp.py                    │
# │ 📄 Archivo: erp.py                                                   │
# └──────────────────────────────────────────────────────────────────────┘
# 🎯 Objetivo: Esquema Pydantic para entrada de credenciales de ERP.
# 📌 Estado: Validado, seguro y compatible con Pydantic v2.

from pydantic import BaseModel

class ErpConfigCreate(BaseModel):
    usuario_api: str
    access_key: str
