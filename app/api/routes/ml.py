
#app/api/routes/ml.py  este codigo lo pasaste hoy 15 de mayo de 2025

from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_async_session
from app.services.ml_token_service import get_valid_access_token
import httpx

router = APIRouter()

@router.get("/ml/user-profile/{user_id}")
async def get_ml_user_profile(user_id: int, db: AsyncSession = Depends(get_async_session)):
    try:
        access_token = await get_valid_access_token(db, user_id)
        headers = {
            "Authorization": f"Bearer {access_token}"
        }

        async with httpx.AsyncClient() as client:
            response = await client.get("https://api.mercadolibre.com/users/me", headers=headers)
            response.raise_for_status()  # lanza excepción si hay error 400/500

        return response.json()

    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
