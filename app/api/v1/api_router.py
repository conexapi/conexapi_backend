# ┌─────────────────────────────────────────────────────────────────────────────┐
# │ 📁 Ubicación: conexapi_backend/app/api/v1/api_router.py                     │
# │ 📄 Archivo: api_router.py                                                   │
# └─────────────────────────────────────────────────────────────────────────────┘
# 🎯 Objetivo: Unificar todos los routers de la API versión 1. Incluye rutas de
# autenticación con SIIGO APIARY y almacenamiento de credenciales en la BD.
# 📌 Estado: Activo y funcional, incluye routers de ERP y autenticación SIIGO.

from fastapi import APIRouter
from app.api.v1.erp.siigo import login_router, erp_router

router = APIRouter()
router.include_router(login_router)
router.include_router(erp_router)
