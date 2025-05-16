#Crear el modelo de SQLAlchemy (para la tabla oauth_tokens)para que podamos interactuar con la base de datos y guardar los tokens.

# app/db/models/oauth.py

from sqlalchemy import Column, Integer, BigInteger, String, Text, TIMESTAMP, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class OAuthToken(Base):
    __tablename__ = "oauth_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, nullable=False)
    platform = Column(String(50), nullable=False)
    access_token = Column(Text, nullable=False)
    token_type = Column(String(50))
    expires_in = Column(Integer)
    scope = Column(Text)
    refresh_token = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        # Restricción única compuesta
        {"sqlite_autoincrement": True},  # (opcional)
    )

    # Definimos la clave única en combinación
    __mapper_args__ = {
        "eager_defaults": True  # Opcional, para que los valores por defecto se carguen automáticamente
    }
