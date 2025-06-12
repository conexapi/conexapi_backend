from sqlalchemy import Column, Integer, String, DateTime, func
from app.db.base import Base  # 👈 Solo importa Base, no al revés

class ErpConfig(Base):
    __tablename__ = "erp_config"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, default="siigo")
    usuario_api = Column(String(150), nullable=False)
    access_key = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
