# Ubicación: /conexapi/backend/app/models.py
# Propósito: Define los modelos de la base de datos (tablas), como la tabla de usuarios.

# Dependencias: SQLAlchemy (declarative_base, Column, Integer, String, Boolean)

from sqlalchemy import Column, Integer, String, Boolean # Tipos de columnas para la DB
from sqlalchemy.ext.declarative import declarative_base # Para la base declarativa

# Importamos Base de main.py, ya que es la instancia de declarative_base que configuramos.
# Esta importación cíclica es común en SQLAlchemy con esta estructura, y FastAPI la maneja bien.
from app.main import Base

# Definición del modelo de usuario
# class User(Base): Define una clase de Python que "mapea" a una tabla en la base de datos.
#                   'Base' es la clase base que SQLAlchemy usa para este mapeo.
class User(Base):
    """
    Modelo de Base de Datos para la tabla de Usuarios.
    Representa a un usuario registrado en el sistema ConexAPI.
    """
    # __tablename__: Atributo obligatorio que especifica el nombre de la tabla en la base de datos.
    __tablename__ = "users"

    # id: Columna para el identificador único del usuario. Es la llave primaria.
    #     Column(Integer, primary_key=True, index=True): Define una columna de tipo entero,
    #     que es la clave primaria de la tabla y sobre la cual se creará un índice para búsquedas rápidas.
    id = Column(Integer, primary_key=True, index=True)

    # email: Columna para el correo electrónico del usuario. Debe ser único y no nulo.
    #        String(255): Columna de texto con un máximo de 255 caracteres.
    #        unique=True: No se pueden tener dos usuarios con el mismo correo.
    #        index=True: Crea un índice para búsquedas rápidas por email.
    email = Column(String(255), unique=True, index=True, nullable=False)

    # hashed_password: Columna para la contraseña hasheada del usuario. No nula.
    #                  Nunca guardamos la contraseña en texto plano, solo su versión hasheada.
    hashed_password = Column(String(255), nullable=False)

    # is_active: Columna booleana para indicar si la cuenta del usuario está activa.
    #            Boolean: Tipo de datos booleano (True/False).
    #            default=True: Por defecto, un usuario nuevo estará activo.
    is_active = Column(Boolean, default=True)

    # __repr__(): Un método especial de Python que define cómo se representa un objeto cuando se imprime.
    #             Útil para depuración.
    def __repr__(self):
        """
        Representación en string del objeto User.
        """
        # f-string: Un string formateado en Python, permite incrustar variables directamente.
        return f"<User(id={self.id}, email='{self.email}')>"

    # Símbolos especiales explicados:
    # Column: Objeto de SQLAlchemy para definir una columna de una tabla de base de datos.
    # Integer, String, Boolean: Tipos de datos de la base de datos.
    # primary_key=True: Indica que esta columna es la clave primaria de la tabla.
    # index=True: Crea un índice en la columna para optimizar las búsquedas.
    # unique=True: Asegura que todos los valores en esta columna sean únicos.
    # nullable=False: Significa que esta columna no puede estar vacía.
    # default=True: El valor por defecto para esta columna si no se especifica uno.