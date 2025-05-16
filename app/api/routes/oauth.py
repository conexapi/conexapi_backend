# app/api/routes/oauth.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.oauth import OAuthTokenCreate, OAuthTokenOut
from app.crud.oauth import create_or_update_oauth_token
from app.db.session import get_async_session
from app.services.ml_token_service import get_valid_access_token

router = APIRouter()

@router.post("/oauth/token", response_model=OAuthTokenOut)
async def save_oauth_token(
    token_data: OAuthTokenCreate,
    db: AsyncSession = Depends(get_async_session)
):
    try:
        token = await create_or_update_oauth_token(db, token_data)
        await db.commit()
        await db.refresh(token)
        return token
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# Paso 1: Crear endpoint de prueba funcional real (temporal o fijo)
#Vamos a añadir un endpoint real que devuelva un access_token siempre válido, usando la función que creamos.

@router.get("/oauth/token/valid/{user_id}")
async def get_token_valid(user_id: int, db: AsyncSession = Depends(get_async_session)):
    try:
        access_token = await get_valid_access_token(db, user_id)
        return {"access_token": access_token}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))