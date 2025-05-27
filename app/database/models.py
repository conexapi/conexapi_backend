# Ubicación: /conexapi/conexapi_backend/app/database/models.py
# Propósito: Define la estructura de las tablas en la base de datos utilizando SQLAlchemy.
#            Cada clase aquí representa una tabla de nuestra base de datos.
# Dependencias: sqlalchemy

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum # <-- ¡NUEVAS IMPORTACIONES!
from sqlalchemy.orm import declarative_base, relationship # <-- ¡NUEVA IMPORTACIÓN: relationship!
from datetime import datetime # <-- ¡NUEVA IMPORTACIÓN!
import enum # <-- ¡NUEVA IMPORTACIÓN!

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
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    # Fecha y hora de la última actualización de la orden
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

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