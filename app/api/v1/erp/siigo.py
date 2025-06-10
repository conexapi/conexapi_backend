# 📁 Ruta: conexapi_backend/app/api/v1/erp/siigo.py  
# 🧾 Archivo: siigo.py  
# 🎯 Objetivo: Gestionar los endpoints relacionados con SIIGO, incluyendo autenticación del cliente mediante APIARY.  
# 📌 Estado: Implementado endpoint `/auth/siigo/login` que valida credenciales contra SIIGO APIARY.

#🔧 Notas adicionales:
#Partner-Id: Es un identificador único proporcionado por SIIGO para cada aplicación que se integra con su API. Debes reemplazar "tu_partner_id" con el valor real asignado a tu aplicación.

#Token de acceso: El token obtenido tiene una vigencia limitada (por ejemplo, 24 horas). Deberás almacenarlo de manera segura y renovarlo cuando expire.

#Manejo de errores: Es recomendable implementar un manejo de errores más robusto para cubrir diferentes escenarios de fallo.


from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_session
from app.schemas.erp import ErpConfigCreate
from app.db.crud.erp import create_or_update_erp_config
from pydantic import BaseModel
import httpx


# Router para autenticación con APIARY
login_router = APIRouter(prefix="/auth/siigo", tags=["SIIGO"])

# Router para persistencia local
erp_router = APIRouter(prefix="/api/v1/erp", tags=["ERP - SIIGO"])


# --- Endpoint: Autenticación con SIIGO APIARY ---
class SiigoLoginRequest(BaseModel):
    usuario_api: str
    access_key: str

@login_router.post("/login")
async def login_siigo(data: SiigoLoginRequest):
    headers = {
        "Content-Type": "application/json",
        "Partner-Id": "tu_partner_id"  # 🔒 Reemplazar en producción
    }
    payload = {
        "username": data.usuario_api,
        "access_key": data.access_key
    }
    url = "https://api.siigo.com/auth/token"

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        return {
            "status": "success",
            "detail": "Autenticación válida",
            "token": response.json().get("access_token")
        }
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales SIIGO inválidas o expiradas",
    )


# --- Endpoint: Guardar credenciales en la BD ---
@erp_router.post("/siigo-auth", status_code=status.HTTP_200_OK)
async def save_siigo_credentials(
    credentials: ErpConfigCreate,
    db: AsyncSession = Depends(get_session),
):
    try:
        await create_or_update_erp_config(db, credentials)
        await db.commit()
        return {"message": "Credenciales SIIGO guardadas correctamente"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al guardar: {str(e)}")
