# Ubicación: /conexapi/conexapi_backend/app/database/models.py
# Propósito: Define la estructura de las tablas en la base de datos utilizando SQLAlchemy.
#            Cada clase aquí representa una tabla de nuestra base de datos.
# Dependencias: sqlalchemy

# Importamos 'timezone' de datetime para usar datetime.now(timezone.utc)
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime, timezone 
import enum

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="regular")

    # Definir la relación inversa con Order.
    # Esto permite acceder a 'user.orders' para obtener las órdenes de un usuario.
    orders = relationship("Order", back_populates="owner") # <-- ¡ESTA LÍNEA ES CLAVE!

    # Nueva relación: Un usuario puede tener múltiples configuraciones de integración
    # o una configuración de integración puede estar asociada a un usuario administrador específico.
    # Por ahora, la hacemos independiente para que la configuración sea global,
    # pero si en el futuro necesitas que cada usuario tenga sus propias credenciales,
    # aquí iría una ForeignKey a User.id y una relationship.
    # Por ahora, mantendremos IntegrationConfig independiente o asociada a un admin para simplificar.

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>" # <-- Opcional: Actualizar repr

# ----- ¡NUEVA CLASE DE MODELO COMPLETA QUE DEBE ESTAR AQUÍ! -----

# 1. Definir un Enum para el estado de la orden (buena práctica para valores fijos)
class OrderStatus(enum.Enum): # <--- ¡ESTO ES LO QUE FALTA EN TU ARCHIVO ACTUAL!
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class Order(Base):
    # Propósito: Representa la tabla 'orders' en la base de datos.
    #            Almacena la información de cada orden de venta.

    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    
    # Campo para identificar la orden externamente (ej. ID de Siigo, MercadoLibre)
    external_id = Column(String, unique=True, index=True, nullable=True) # ID de la orden en el sistema externo

    # Estado de la orden (usando el Enum que definimos)
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING, nullable=False)

    # Fecha y hora de creación de la orden
    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc), nullable=False)

    # Cantidad total de la orden (ej. 10 unidades de productos)
    total_quantity = Column(Integer, default=0, nullable=False)
    # Valor total de la orden
    total_amount = Column(Float, default=0.0, nullable=False)

    # Relación con el usuario que creó la orden
    # ForeignKey indica que esta columna es una clave foránea a la tabla 'users', columna 'id'.
    owner_id = Column(Integer, ForeignKey("users.id")) # <-- ¡Clave foránea!

    # Define la relación entre Order y User.
    # 'owner' es el objeto User asociado a esta orden.
    # 'back_populates' conecta con la 'orders' en la clase User.
    owner = relationship("User", back_populates="orders")

    def __repr__(self):
        return f"<Order(id={self.id}, external_id='{self.external_id}', status='{self.status.value}', owner_id={self.owner_id})>"

# ---------------------------------------------

# --- ¡NUEVA CLASE DE MODELO PARA CREDENCIALES DE INTEGRACIÓN! ---
# Ubicación: /conexapi/conexapi_backend/app/database/models.py

class IntegrationConfig(Base):
    __tablename__ = "integration_configs"

    id = Column(Integer, primary_key=True, index=True)
    platform_name = Column(String, unique=True, index=True, nullable=False) # Ej: "SIIGO", "MERCADOLIBRE"
    api_key_or_username = Column(String, nullable=False) # Para Siigo: "Username", para ML: "Client ID" (nuestro)
    access_key_or_secret = Column(String, nullable=False) # Para Siigo: "Access Key", para ML: "Client Secret" (nuestro)
    # Estos campos son para credenciales dinámicas que el usuario final provee:
    # Para ML (OAuth 2.0):
    ml_access_token = Column(String, nullable=True)
    ml_refresh_token = Column(String, nullable=True)
    ml_token_expires_at = Column(DateTime, nullable=True) # Cuándo expira el access_token de ML
    
    # Podríamos añadir una relación si quisiéramos que cada integración estuviera asociada a un usuario específico
    # owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    # owner = relationship("User")

    is_active = Column(Boolean, default=True) # Para activar/desactivar la integración
    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc), nullable=False)

    def __repr__(self):
        return f"<IntegrationConfig(id={self.id}, platform='{self.platform_name}', active={self.is_active})>"
