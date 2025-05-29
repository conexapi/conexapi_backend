# Guardar como: /conexapi/conexapi_backend/test_siigo_mock_token.py

import sys
import os

# --- LÍNEAS IMPORTANTES PARA LA IMPORTACIÓN ---
# Añade el directorio raíz del proyecto (conexapi_backend) a la ruta de búsqueda de módulos de Python.
# Esto es necesario para que las importaciones como 'from app.database import models' funcionen
# cuando el script se ejecuta directamente desde la raíz del proyecto.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
# --- FIN LÍNEAS IMPORTANTES PARA LA IMPORTACIÓN ---

from sqlalchemy.orm import Session
from app.database.database import get_db, SessionLocal, Base, engine # Importa get_db desde database.py
from app.database import models # Tu modelo IntegrationConfig
from app.services.siigo import get_siigo_token # La función que queremos probar
from datetime import datetime, timezone # Necesario si lo usas en el script directamente (aunque la función ya lo usa)


def test_siigo_mock_token():
    """
    Función de prueba para obtener un token del servidor mock de Siigo
    utilizando las credenciales de la base de datos.
    """
    db: Session = next(get_db()) # Obtiene una sesión de base de datos
    
    # IMPORTANTE: Asegúrate de que este ID sea el que se creó para SIIGO
    # (En tu caso, si lo creaste recién, debe ser 1)
    SIIGO_CONFIG_ID_IN_DB = 1 
    siigo_config = db.query(models.IntegrationConfig).filter(models.IntegrationConfig.id == SIIGO_CONFIG_ID_IN_DB).first() 

    if siigo_config:
        print(f"Intentando obtener token de Siigo Mock para config ID: {siigo_config.id}")
        # Llama a tu función principal de servicio
        updated_config = get_siigo_token(db, siigo_config)
        
        if updated_config and updated_config.ml_access_token:
            print(f"¡Token de Siigo Mock obtenido con éxito! Token: {updated_config.ml_access_token[:20]}...") # Imprime solo una parte
            print(f"Expira en: {updated_config.ml_token_expires_at}")
        else:
            print("Fallo al obtener token de Siigo Mock.")
    else:
        print(f"ERROR: No se encontró la configuración de Siigo en la base de datos con el ID: {SIIGO_CONFIG_ID_IN_DB}. Por favor, verifica el ID o crea la entrada SIIGO primero.")
    
    db.close() # Cierra la sesión de la base de datos al finalizar

if __name__ == "__main__":
    print("--- Iniciando prueba de token de Siigo Mock ---")
    test_siigo_mock_token()
    print("--- Prueba finalizada ---")