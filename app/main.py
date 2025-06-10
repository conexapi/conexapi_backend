# ┌─────────────────────────────────────────────────────────────────────────────┐
# │ 📁 Ubicación: conexapi_backend/app/main.py                                  │
# │ 📄 Archivo: main.py                                                         │
# └─────────────────────────────────────────────────────────────────────────────┘
# 🎯 Objetivo: Punto de entrada principal de FastAPI. Monta routers y define
# endpoint `/health` para validar conexión a base de datos.
# 📌 Estado: Funcional y listo para ejecución (modo desarrollo).

from fastapi import FastAPI
from app.db.session import engine
from app.api.v1 import api_router
from sqlalchemy import text

app = FastAPI(
    title="ConexAPI",
    version="1.0.0",
    description="Middleware ERP ↔ Marketplace - SIIGO & MercadoLibre"
)

# Endpoint simple para verificar conexión a la BD
@app.get("/health")
async def health_check():
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return {"status": "ok", "db": "connected"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}

# Incluir rutas de API
app.include_router(api_router.router)
