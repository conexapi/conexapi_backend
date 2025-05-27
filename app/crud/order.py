# Ubicación: /conexapi/conexapi_backend/app/crud/order.py
# Propósito: Contiene funciones para interactuar con la tabla 'orders' en la base de datos.
#            Proporciona operaciones CRUD (Crear, Leer, Actualizar, Eliminar) para las órdenes.
# Dependencias: sqlalchemy.orm.Session, app.database.models, app.schemas.order

from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete # <-- ¡NUEVAS IMPORTACIONES!

from app.database import models
from app.schemas import order as schemas_order # Renombrado para evitar conflicto con 'order'


# Función para crear una nueva orden en la base de datos
def create_order(db: Session, order: schemas_order.OrderCreate, owner_id: int):
    # Propósito: Guarda una nueva orden de venta en la base de datos.
    # Parámetros:
    #   - db (Session): La sesión de base de datos actual.
    #   - order (schemas_order.OrderCreate): El esquema Pydantic con los datos de la orden.
    #   - owner_id (int): El ID del usuario que es propietario de esta orden.
    # Retorno:
    #   - models.Order: El objeto Order de SQLAlchemy recién creado y guardado.

    # Creamos una instancia del modelo Order, mapeando los datos del esquema.
    # Los campos created_at y updated_at se generarán automáticamente por el modelo.
    db_order = models.Order(
        external_id=order.external_id,
        status=order.status,
        total_quantity=order.total_quantity,
        total_amount=order.total_amount,
        owner_id=owner_id # Asignamos el propietario de la orden
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order) # Actualiza el objeto con el ID generado por la DB
    return db_order

# Función para obtener una orden por su ID
def get_order(db: Session, order_id: int):
    # Propósito: Recupera una orden de venta específica por su ID.
    # Parámetros:
    #   - db (Session): La sesión de base de datos actual.
    #   - order_id (int): El ID de la orden a buscar.
    # Retorno:
    #   - models.Order | None: El objeto Order si se encuentra, None en caso contrario.
    return db.scalar(select(models.Order).where(models.Order.id == order_id))

# Función para obtener múltiples órdenes
def get_orders(db: Session, skip: int = 0, limit: int = 100):
    # Propósito: Recupera una lista de órdenes de venta.
    # Parámetros:
    #   - db (Session): La sesión de base de datos actual.
    #   - skip (int): Número de registros a omitir (para paginación).
    #   - limit (int): Número máximo de registros a devolver (para paginación).
    # Retorno:
    #   - list[models.Order]: Una lista de objetos Order.
    return db.scalars(select(models.Order).offset(skip).limit(limit)).all()

# Función para obtener órdenes de un usuario específico
def get_user_orders(db: Session, owner_id: int, skip: int = 0, limit: int = 100):
    # Propósito: Recupera una lista de órdenes que pertenecen a un usuario específico.
    # Parámetros:
    #   - db (Session): La sesión de base de datos actual.
    #   - owner_id (int): El ID del usuario cuyas órdenes se quieren recuperar.
    #   - skip (int): Número de registros a omitir (para paginación).
    #   - limit (int): Número máximo de registros a devolver (para paginación).
    # Retorno:
    #   - list[models.Order]: Una lista de objetos Order.
    return db.scalars(
        select(models.Order)
        .where(models.Order.owner_id == owner_id)
        .offset(skip)
        .limit(limit)
    ).all()


# Función para actualizar una orden existente
def update_order(db: Session, order_id: int, order_update: schemas_order.OrderUpdate):
    # Propósito: Actualiza los campos de una orden existente en la base de datos.
    # Parámetros:
    #   - db (Session): La sesión de base de datos actual.
    #   - order_id (int): El ID de la orden a actualizar.
    #   - order_update (schemas_order.OrderUpdate): Esquema con los campos a actualizar.
    # Retorno:
    #   - models.Order | None: El objeto Order actualizado si se encuentra, None en caso contrario.

    # 1. Preparar los datos para la actualización: solo los campos que no son None.
    update_data = order_update.model_dump(exclude_unset=True)
    
    # 2. Si hay datos para actualizar, ejecutar la actualización.
    if update_data:
        # Crea la sentencia UPDATE para la orden específica por ID.
        stmt = update(models.Order).where(models.Order.id == order_id).values(**update_data)
        db.execute(stmt)
        db.commit() # Confirma los cambios en la base de datos

    # 3. Recuperar y devolver la orden actualizada (para asegurar que tenemos el último estado).
    # Esto es importante porque 'onupdate' puede haber cambiado 'updated_at'.
    return get_order(db, order_id)

# Función para eliminar una orden
def delete_order(db: Session, order_id: int):
    # Propósito: Elimina una orden de venta de la base de datos.
    # Parámetros:
    #   - db (Session): La sesión de base de datos actual.
    #   - order_id (int): El ID de la orden a eliminar.
    # Retorno:
    #   - models.Order | None: El objeto Order eliminado si se encuentra y se elimina, None en caso contrario.

    # Recupera la orden para verificar su existencia antes de eliminar
    db_order = get_order(db, order_id)
    if db_order:
        # Crea la sentencia DELETE para la orden específica por ID.
        stmt = delete(models.Order).where(models.Order.id == order_id)
        db.execute(stmt)
        db.commit() # Confirma los cambios en la base de datos
        return db_order # Devuelve el objeto que fue eliminado
    return None