#/app/services/ml_token_service.py

from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.oauth import OAuthToken
from app.schemas.oauth import OAuthTokenCreate
from app.crud.oauth import create_or_update_oauth_token
from app.utils.token import refresh_access_token


async def get_valid_access_token(db: AsyncSession, user_id: int, platform: str = "mercadolibre") -> str:
    """
    Obtiene un access_token válido. Si está por expirar (menos de 5 min), lo renueva automáticamente.
    """
    stmt = select(OAuthToken).where(
        OAuthToken.user_id == user_id,
        OAuthToken.platform == platform
    )
    result = await db.execute(stmt)
    token: OAuthToken = result.scalars().first()

    if not token:
        raise Exception(f"No hay token OAuth registrado para el usuario {user_id} en {platform}")

    now = datetime.now(timezone.utc)
    threshold = timedelta(minutes=5)

    # Si el token está por expirar (o expirado), renovarlo
    if not token.expires_at or token.expires_at <= (now + threshold):
        refresh_response = await refresh_access_token(token.refresh_token)

        if "error" in refresh_response:
            raise Exception(f"Error al refrescar token: {refresh_response['error']} | Detalles: {refresh_response.get('details')}")

        token_data = OAuthTokenCreate(
            user_id=user_id,
            platform=platform,
            access_token=refresh_response["access_token"],
            refresh_token=refresh_response["refresh_token"],
            expires_in=refresh_response["expires_in"],
            token_type=refresh_response.get("token_type"),
            scope=refresh_response.get("scope"),
        )

        await create_or_update_oauth_token(db, token_data)
        await db.commit()

        return refresh_response["access_token"]

    return token.access_token
