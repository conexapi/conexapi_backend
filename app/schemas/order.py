# Ubicación: /conexapi/conexapi_backend/app/schemas/order.py
# Propósito: Define la estructura (esquemas) de los datos que usaremos para crear,
#            leer y actualizar órdenes de venta.
# Dependencias: pydantic, datetime, app.database.models

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

# Importamos el Enum OrderStatus de nuestro modelo para usarlo en los esquemas.
from app.database.models import OrderStatus

# Esquema base para los campos comunes de una orden.
class OrderBase(BaseModel):
    # external_id es opcional porque quizás algunas órdenes se creen internamente
    # o su ID externo no se conoce al principio.
    external_id: Optional[str] = None
    
    # El status puede ser provisto al crear/actualizar, pero tendremos un default en el modelo.
    # Usamos Field con un valor por defecto si queremos que Pydantic lo maneje,
    # pero OrderStatus(value) garantiza que sea uno de los valores del enum.
    status: OrderStatus = OrderStatus.PENDING 
    
    total_quantity: int = Field(default=0, ge=0) # Cantidad total de ítems (>= 0)
    total_amount: float = Field(default=0.0, ge=0.0) # Monto total (>= 0.0)

# Esquema para la creación de una nueva orden.
# Hereda de OrderBase. owner_id no se incluye aquí porque será determinado por el usuario autenticado.
class OrderCreate(OrderBase):
    pass # No hay campos adicionales específicos para la creación más allá de OrderBase por ahora.

# Esquema para la actualización de una orden existente.
# Todos los campos son opcionales para permitir actualizaciones parciales.
class OrderUpdate(BaseModel):
    external_id: Optional[str] = None
    status: Optional[OrderStatus] = None
    total_quantity: Optional[int] = Field(default=None, ge=0)
    total_amount: Optional[float] = Field(default=None, ge=0.0)

# Esquema para representar una orden tal como se lee desde la base de datos (con ID y fechas).
# Incluye el owner_id y los campos de fecha y hora que son generados por la DB.
class OrderInDB(OrderBase):
    id: int
    owner_id: int # El ID del usuario propietario de la orden
    created_at: datetime
    updated_at: datetime

    class Config:
        # Permite que este esquema Pydantic se adapte a un objeto SQLAlchemy (Order model).
        from_attributes = True

# Esquema para mostrar la orden con la información básica de su propietario (User).
# Útil cuando queremos devolver una orden y también mostrar quién es su dueño.
class OrderResponse(OrderInDB):
    # Aquí podríamos incluir un esquema reducido del usuario si queremos
    # que la respuesta de la orden incluya información del owner.
    # Por ahora, mantendremos owner_id, pero si quisieras el email del owner, podrías hacer:
    # owner: 'schemas_user.UserInDB' # Requiere importación de schemas_user y un update_forward_refs
    pass