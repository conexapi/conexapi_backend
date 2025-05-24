# Ubicación: /conexapi/conexapi_backend/app/main.py
# Propósito: Es el punto de entrada principal para nuestra aplicación FastAPI.
#            Aquí inicializamos FastAPI y ejecutamos operaciones de base de datos.
# Dependencias: fastapi, database

from fastapi import FastAPI
from app.database.database import create_db_and_tables
from app.api import auth

# Inicializa la aplicación FastAPI.
app = FastAPI()
app.include_router(auth.router)

@app.on_event("startup")
async def startup_event():
    # Propósito: Función que se ejecuta automáticamente cuando la aplicación FastAPI arranca.
    #            Es el lugar ideal para tareas de inicialización, como crear las tablas de la base de datos.
    # **: El operador "**" se usa en Python para pasar argumentos de palabras clave (keyword arguments)
    #    a una función. Aquí no se usa directamente, pero se menciona como símbolo especial.
    # *args: El operador "*" se usa para pasar un número variable de argumentos posicionales.
    #        Aquí no se usa directamente, pero se menciona como símbolo especial.
    print("Iniciando la aplicación y creando tablas de base de datos...")
    create_db_and_tables()
    print("Aplicación iniciada. Tablas verificadas.")

@app.get("/")
async def read_root():
    # Propósito: Un endpoint de prueba simple para verificar que la API está funcionando.
    #            Cuando accedes a la raíz de la API (por ejemplo, http://localhost:8000/),
    #            esta función se ejecuta y devuelve un mensaje.
    # -> (dict[str, str]): La flecha indica que esta función devuelve un diccionario
    #                      donde las claves y los valores son cadenas de texto.
    return {"message": "¡ConexAPI Backend funcionando!"}