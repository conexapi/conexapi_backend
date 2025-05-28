# Ubicación: /conexapi/conexapi_backend/app/schemas/user.py
# Propósito: Define la estructura (esquemas) de los datos que usaremos para crear usuarios,
#            loguearse y para representar un usuario en la respuesta de la API.
# Dependencias: pydantic

from typing import Optional
from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    # Propósito: Esquema base para un usuario, contiene campos comunes como el email.
    # Responsabilidades: Asegurar que el email tenga el formato correcto.
    email: EmailStr
    # email (EmailStr): El correo electrónico del usuario. EmailStr de Pydantic
    #                   valida automáticamente que sea un email válido.

class UserCreate(UserBase):
    # Propósito: Esquema para crear un nuevo usuario. Hereda de UserBase y añade la contraseña.
    # Responsabilidades: Asegurar que la contraseña sea una cadena de texto.
    password: str
    # password (str): La contraseña del usuario (en texto plano antes de ser cifrada).

    # role: str = "regular" # Si quieres que el frontend pueda sugerir un rol al registrarse.
                           # Sin embargo, generalmente el rol se asigna en el backend.
                           # Lo dejamos comentado por ahora, el backend lo manejará.
class UserUpdate(BaseModel):
    # Permite actualizar solo email, password o role. Todos son opcionales.
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[str] = None # Solo admin debería cambiar esto

class UserInDB(UserBase):
    # Propósito: Esquema para representar un usuario tal como se guarda en la base de datos.
    #            Contiene el ID y la contraseña ya cifrada (hashed).
    # Responsabilidades: Reflejar la estructura de la tabla 'users'.
    id: int
    # id (int): El ID único del usuario en la base de datos.
    hashed_password: str
    # hashed_password (str): La contraseña del usuario ya cifrada (hashed).

    role: str # Incluir el rol en el esquema que representa al usuario de la DB.

    class Config:
        # Propósito: Configuración interna de Pydantic para este modelo.
        # Responsabilidades: Permite que el modelo se adapte a objetos de SQLAlchemy.
        from_attributes = True
        # from_attributes (bool): Símbolo especial. Le dice a Pydantic que intente leer
        #                         los datos de objetos que no son diccionarios (como los objetos de SQLAlchemy).


#Se añade la clase TokenData que simplemente espera un campo username (que es el sub de nuestro token). Esto ayuda a Pydantic a validar que el payload del token tenga la estructura esperada.
class TokenData(BaseModel):
    # Propósito: Esquema para validar los datos que se extraen del payload de un token JWT.
    #            Contiene el identificador del usuario (username/email) que se usó en el token.
    username: str | None = None # <-- ¡NUEVA LÍNEA!
    # username (str | None): El identificador del usuario (nuestro email) que se espera en el token.
    #                        Puede ser None si el token no contiene esta información.
