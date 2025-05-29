# Guardar como: /conexapi/conexapi_backend/test_siigo_mock_token.py

import sys
import os

# --- INICIO LÍNEAS DE DEPURACIÓN DE RUTA ---
print(f"DEBUG: os.getcwd() (Current Working Directory): {os.getcwd()}") # Dónde crees que estás ejecutando
print(f"DEBUG: __file__ (Location of this script): {os.path.abspath(__file__)}")

current_script_dir = os.path.dirname(os.path.abspath(__file__))
print(f"DEBUG: Calculated current_script_dir (Project Root Candidate): {current_script_dir}")

# Añade el directorio raíz del proyecto (conexapi_backend) al sys.path
# Esto es esencial para que Python encuentre 'app' como un paquete de nivel superior.
if current_script_dir not in sys.path:
    sys.path.insert(0, current_script_dir)
    print(f"DEBUG: ADDED '{current_script_dir}' to sys.path.")
else:
    print(f"DEBUG: '{current_script_dir}' was already in sys.path.")

print(f"DEBUG: sys.path (AFTER modifications):")
for i, p in enumerate(sys.path):
    print(f"  [{i}] {p}")

# Verificaciones directas de existencia de archivos/directorios clave
app_dir_path = os.path.join(current_script_dir, 'app')
services_dir_path = os.path.join(app_dir_path, 'services')
siigo_file_path = os.path.join(services_dir_path, 'siigo.py')
app_init_path = os.path.join(app_dir_path, '__init__.py')
services_init_path = os.path.join(services_dir_path, '__init__.py')


print(f"DEBUG: Check 'app' directory: {app_dir_path} -> Exists: {os.path.exists(app_dir_path)}")
print(f"DEBUG: Check 'app/__init__.py': {app_init_path} -> Exists: {os.path.exists(app_init_path)}")
print(f"DEBUG: Check 'app/services' directory: {services_dir_path} -> Exists: {os.path.exists(services_dir_path)}")
print(f"DEBUG: Check 'app/services/__init__.py': {services_init_path} -> Exists: {os.path.exists(services_init_path)}")
print(f"DEBUG: Check 'app/services/siigo.py': {siigo_file_path} -> Exists: {os.path.exists(siigo_file_path)}")
# --- FIN LÍNEAS DE DEPURACIÓN DE RUTA ---


# Estas importaciones ahora deberían funcionar si la ruta está bien y los __init__.py existen
from sqlalchemy.orm import Session
from app.database.database import get_db, SessionLocal, Base, engine
from app.database import models
from app.services.siigo import get_siigo_token # La línea que da el error


def test_siigo_mock_token():
    """
    Función de prueba para obtener un token del servidor mock de Siigo
    utilizando las credenciales de la base de datos.
    """
    db: Session = next(get_db())
    
    SIIGO_CONFIG_ID_IN_DB = 1
    siigo_config = db.query(models.IntegrationConfig).filter(models.IntegrationConfig.id == SIIGO_CONFIG_ID_IN_DB).first()

    if siigo_config:
        print(f"Intentando obtener token de Siigo Mock para config ID: {siigo_config.id}")
        updated_config = get_siigo_token(db, siigo_config)
        
        if updated_config and updated_config.ml_access_token:
            print(f"¡Token de Siigo Mock obtenido con éxito! Token: {updated_config.ml_access_token[:20]}...")
            print(f"Expira en: {updated_config.ml_token_expires_at}")
        else:
            print("Fallo al obtener token de Siigo Mock.")
    else:
        print(f"ERROR: No se encontró la configuración de Siigo en la base de datos con el ID: {SIIGO_CONFIG_ID_IN_DB}. Por favor, verifica el ID o crea la entrada SIIGO primero.")
    
    db.close()

if __name__ == "__main__":
    print("--- Iniciando prueba de token de Siigo Mock ---")
    test_siigo_mock_token()
    print("--- Prueba finalizada ---")