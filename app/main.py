# Ubicación: /conexapi/conexapi_backend/app/main.py

from contextlib import asynccontextmanager
from fastapi import FastAPI
# CORRECCIÓN DE LA LÍNEA DE IMPORTACIÓN:
from app.database.database import create_db_and_tables # <-- ¡AHORA SÍ ES CORRECTO AQUÍ!
from app.api import auth
from app.api import users

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Iniciando la aplicación y creando tablas de base de datos...")
    create_db_and_tables()
    print("Aplicación iniciada. Tablas verificadas.")
    yield
    print("Apagando la aplicación...")

app = FastAPI(lifespan=lifespan)
app.include_router(auth.router)
app.include_router(users.router)

@app.get("/")
async def read_root():
    return {"message": "¡ConexAPI Backend funcionando!"}