# Ubicación: /conexapi/backend/app/schemas.py
# Propósito: Define la estructura de los datos (esquemas) que nuestra API espera recibir
#              y los que enviará, usando Pydantic para validación.

# Dependencias: Pydantic (BaseModel, EmailStr)

from pydantic import BaseModel, EmailStr # BaseModel para crear esquemas, EmailStr para validar correos

# Esquema para el registro de un nuevo usuario
class UserCreate(BaseModel):
    """
    Esquema para crear un nuevo usuario.
    Define los campos que se esperan cuando un usuario se registra.
    """
    email: EmailStr # email: Debe ser un string con formato de correo electrónico válido.
    password: str   # password: Un string para la contraseña.

# Esquema para la información de un usuario en la respuesta de la API (sin la contraseña)
class UserInDB(BaseModel):
    """
    Esquema para un usuario tal como se almacena en la base de datos
    (incluye el ID y si está activo).
    """
    id: int
    email: EmailStr
    is_active: bool

    # Config: Una clase interna de Pydantic para configuraciones adicionales del esquema.
    class Config:
        # orm_mode = True (ahora from_orm = True en Pydantic v2+):
        # Permite que el esquema Pydantic lea datos directamente de un objeto de ORM (como nuestro modelo SQLAlchemy).
        # Esto significa que podemos pasar una instancia de nuestro modelo 'User' (de models.py)
        # y Pydantic la convertirá automáticamente a este esquema.
        from_attributes = True # Equivalente a orm_mode = True en Pydantic v1.

# Esquema para la respuesta de un token (cuando el usuario inicia sesión)
class Token(BaseModel):
    """
    Esquema para el token de acceso JWT y el tipo de token.
    """
    access_token: str   # access_token: El JWT real.
    token_type: str = "bearer" # token_type: El tipo de token, comúnmente "bearer".

# Esquema para los datos del token JWT (lo que se "guarda" dentro del token)
class TokenData(BaseModel):
    """
    Esquema para los datos que se codifican dentro del JWT.
    Normalmente, solo el "sub" (subject), que es el identificador del usuario.
    """
    email: str | None = None # email: El correo electrónico del usuario, opcional.
    # | None: Esto es una "unión de tipos" en Python 3.10+. Significa que el tipo puede ser 'str' O 'None'.
    # = None: Indica que es opcional y su valor por defecto es None.

    # Símbolos especiales explicados:
    # EmailStr: Un tipo especial de Pydantic que valida si el string es un formato de correo electrónico válido.
    # BaseModel: Clase base de Pydantic para crear esquemas de datos.
    # str | None: Anotación de tipo que significa "string o None".
    # = None: Asigna un valor predeterminado de None, haciendo el campo opcional.