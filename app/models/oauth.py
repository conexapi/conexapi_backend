# app/models/oauth.py

from sqlalchemy import Column, Integer, String, Text, BigInteger, TIMESTAMP, func, UniqueConstraint
#from sqlalchemy import expression
from app.db.base import Base  # Asegúrate que este es tu Base declarativa
from datetime import datetime, timedelta



class OAuthToken(Base):
    __tablename__ = "oauth_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, nullable=False)
    platform = Column(String(50), nullable=False)
    access_token = Column(Text, nullable=False)
    token_type = Column(String(50), nullable=True)
    expires_in = Column(Integer, nullable=True)
    scope = Column(Text, nullable=True)
    refresh_token = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), 
    onupdate=func.now())
    expires_at = Column(TIMESTAMP(timezone=True), nullable=True)  

    __table_args__ = (
        UniqueConstraint("user_id", "platform", name="uix_user_platform"),
        {"sqlite_autoincrement": True}
    )
