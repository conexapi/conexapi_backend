# Ubicación: /conexapi/conexapi_backend/app/database/models.py
# Propósito: Define la estructura de las tablas en la base de datos utilizando SQLAlchemy.
#            Cada clase aquí representa una tabla de nuestra base de datos.
# Dependencias: sqlalchemy

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

# Símbolo especial: declarative_base() es una función de SQLAlchemy que devuelve una clase base
#                   para nuestros modelos declarativos. Es la base de nuestras tablas.
Base = declarative_base()

class User(Base):
    # Propósito: Representa la tabla 'users' en la base de datos.
    #            Aquí guardaremos la información de los usuarios registrados en el sistema.
    # Responsabilidades: Almacenar ID, email y contraseña cifrada de los usuarios.

    __tablename__ = "users"
    # __tablename__ (str): Símbolo especial que le dice a SQLAlchemy cómo se llamará la tabla
    #                      en la base de datos. En este caso, 'users'.

    id = Column(Integer, primary_key=True, index=True)
    # id (Column): La columna 'id'. Es un número entero, la clave principal de la tabla
    #              (identificador único para cada usuario) y tiene un índice para búsquedas rápidas.

    email = Column(String, unique=True, index=True)
    # email (Column): La columna 'email'. Es un texto (String), debe ser único para cada usuario
    #                 (no pueden haber dos usuarios con el mismo email) y también tiene un índice.

    hashed_password = Column(String)
    # hashed_password (Column): La columna para la contraseña. Es un texto (String) y almacenará
    #                           la contraseña cifrada (nunca la contraseña real por seguridad).

    def __repr__(self):
        # Propósito: Método especial que define cómo se representa un objeto User cuando lo imprimimos.
        #            Ayuda a depurar mostrando información legible del usuario.
        return f"<User(id={self.id}, email='{self.email}')>"