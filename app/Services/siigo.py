# Ubicación: /conexapi/conexapi_backend/app/services/siigo.py

import requests
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session
from app.database import models
from app.crud import integration as crud_integration
from app.schemas import integration as schemas_integration
from app.config import settings

# --- FUNCIONES DE AUTENTICACIÓN/OBTENCIÓN DE TOKENS PARA SIIGO ---

def get_siigo_token(db: Session, config: models.IntegrationConfig) -> Optional[models.IntegrationConfig]:
    """
    Obtiene un token de acceso para Siigo Cloud.
    Utiliza las credenciales de la aplicación (client_id y client_secret) desde app.config
    y las credenciales de la cuenta del cliente (username y access_key) desde la config.
    """
    # Obtenemos los valores de settings. Esto no debería ser ColumnElement.
    client_id_val = settings.SIIGO_CLIENT_ID
    client_secret_val = settings.SIIGO_CLIENT_SECRET
    
    # Obtenemos los valores de la configuración de integración (modelo ORM)
    username_value = config.api_key_or_username
    access_key_value = config.access_key_or_secret

    # CORRECCIÓN CLAVE AQUÍ: Verificaciones explícitas para Pylance
    # Para strings (que pueden ser None o vacíos)
    if (client_id_val is None or client_id_val == "" or
        client_secret_val is None or client_secret_val == "" or
        username_value is None or username_value == "" or
        access_key_value is None or access_key_value == ""):
        print(f"Error: Credenciales de Siigo incompletas o vacías para config {config.id}. "
              f"Verifique settings.SIIGO_CLIENT_ID, settings.SIIGO_SECRET_KEY, "
              f"config.api_key_or_username, config.access_key_or_secret.")
        return None

    token_url = "https://api.siigo.com/auth" # Verifica esta URL en la documentación de Siigo
    headers = {"Content-Type": "application/json"}
    data = {
        "username": username_value,
        "access_key": access_key_value,
        "client_id": client_id_val,
        "client_secret": client_secret_val
    }

    try:
        response = requests.post(token_url, headers=headers, json=data)
        response.raise_for_status()
        token_data = response.json()

        # Usamos los campos ml_access_token y ml_token_expires_at para almacenar el token de Siigo
        # Idealmente, models.IntegrationConfig y schemas.IntegrationConfigTokenUpdate
        # tendrían campos específicos para Siigo si la autenticación es diferente.
        # Por ahora, usamos los campos existentes para no introducir nuevos errores.
        update_schema = schemas_integration.IntegrationConfigTokenUpdate(
            ml_access_token=token_data.get("access_token"), # Asumo que Siigo devuelve 'access_token'
            ml_token_expires_at=datetime.now(timezone.utc) + timedelta(seconds=token_data.get("expires_in", 3600))
        )

        # Aquí, el argumento para update_integration_config debe ser config_update_data
        # crud_integration.update_integration_config espera config_update_data
        updated_config = crud_integration.update_integration_config(db, config.id, config_update_data=update_schema)
        if updated_config is None: # Usar 'is None' para verificar si el objeto se actualizó correctamente
            print(f"Advertencia: No se pudo actualizar la configuración de Siigo {config.id} en la base de datos.")
        return updated_config

    except requests.exceptions.RequestException as e:
        print(f"Error al obtener token de Siigo: {e}")
        return None
    except Exception as e:
        print(f"Error inesperado al procesar token de Siigo: {e}")
        return None

def is_siigo_token_expired(config: models.IntegrationConfig) -> bool:
    """
    Verifica si el token de acceso de Siigo ha expirado.
    """
    # Esta función asume que el token de Siigo se guarda en ml_token_expires_at
    if config.ml_token_expires_at is None: # Esta verificación ya es correcta y explícita para Pylance
        return True

    safety_margin = timedelta(minutes=1)
    # La comparación de datetime con datetime debería estar bien para Pylance.
    return datetime.now(timezone.utc) + safety_margin >= config.ml_token_expires_at

# --- FUNCIONES DE INTERACCIÓN CON LA API DE SIIGO ---

def create_siigo_invoice(access_token: str, invoice_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    invoice_url = "https://api.siigo.com/v1/invoices" # Verifica esta URL
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json", "Accept": "application/json"}
    try:
        response = requests.post(invoice_url, headers=headers, json=invoice_data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error al crear factura en Siigo: {e}")
        return None

def get_siigo_products(access_token: str) -> List[Dict[str, Any]]:
    products_url = "https://api.siigo.com/v1/products" # Verifica esta URL
    headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}
    try:
        response = requests.get(products_url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener productos de Siigo: {e}")
        return []

def sync_siigo_inventory(access_token: str, product_code: str, new_quantity: int) -> bool:
    # Esta URL y el formato de datos son ejemplos; consulta la doc de Siigo.
    inventory_update_url = f"https://api.siigo.com/v1/products/{product_code}/inventory"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json", "Accept": "application/json"}
    data = {"quantity": new_quantity}
    try:
        response = requests.patch(inventory_update_url, headers=headers, json=data) # O PUT, según Siigo
        response.raise_for_status()
        print(f"Sincronización de inventario para {product_code} en Siigo exitosa.")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error al sincronizar inventario de {product_code} en Siigo: {e}")
        return False