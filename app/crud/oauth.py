# app/crud/oauth.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.oauth import OAuthToken
from app.schemas.oauth import OAuthTokenCreate
from sqlalchemy.exc import IntegrityError
from sqlalchemy import update
from datetime import datetime, timedelta, timezone

async def create_or_update_oauth_token(db: AsyncSession, token_data: OAuthTokenCreate):
    stmt = select(OAuthToken).where(
        OAuthToken.user_id == token_data.user_id,
        OAuthToken.platform == token_data.platform  # Asignar valor por defecto si no viene
    )
    result = await db.execute(stmt)
    token = result.scalars().first()

    expires_at = datetime.now(timezone.utc) + timedelta(seconds=token_data.expires_in or 21600)

    if token:
        # Si ya existe, actualiza
        token.access_token = token_data.access_token
        token.token_type = token_data.token_type
        token.expires_in = token_data.expires_in
        token.scope = token_data.scope
        token.refresh_token = token_data.refresh_token
        token.expires_at = expires_at
        return token
    else:
        # Si no existe, crea nuevo
        new_token = OAuthToken(**token_data.model_dump(), expires_at=expires_at)
        db.add(new_token)
        return new_token
