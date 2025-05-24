# Ubicación: /conexapi/conexapi_backend/app/main.py
# Propósito: Es el punto de entrada principal para nuestra aplicación FastAPI.
#            Aquí inicializamos FastAPI, ejecutamos operaciones de base de datos
#            y "conectamos" los routers de nuestra API.
# Dependencias: fastapi, app.database.database, app.api.auth

from fastapi import FastAPI
from app.database.database import create_db_and_tables
from app.api import auth # <-- ¡NUEVA LÍNEA! Importa el router de autenticación

# Inicializa la aplicación FastAPI.
app = FastAPI()

# Símbolo especial: app.include_router(). Conecta un router de FastAPI (como el de autenticación)
#                   a la aplicación principal. Esto hace que todos los endpoints definidos
#                   en 'auth.py' estén disponibles a través de nuestra API principal.
app.include_router(auth.router) # <-- ¡NUEVA LÍNEA!

@app.on_event("startup")
async def startup_event():
    # Propósito: Función que se ejecuta automáticamente cuando la aplicación FastAPI arranca.
    #            Es el lugar ideal para tareas de inicialización, como crear las tablas de la base de datos.
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