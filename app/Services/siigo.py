# Ubicación: /conexapi/conexapi_backend/app/services/siigo.py

import requests
from typing import Optional, Dict, Any, List, cast
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
    client_id_val = settings.SIIGO_CLIENT_ID
    client_secret_val = settings.SIIGO_CLIENT_SECRET
    partner_id_val = settings.SIIGO_PARTNER_ID
    
    username_value = config.api_key_or_username
    access_key_value = config.access_key_or_secret

    if (username_value is None or cast(str, username_value) == "" or
        access_key_value is None or cast(str, access_key_value) == ""):
        print(f"Error: Username o Access Key incompletos o vacíos para config {config.id}. "
              f"Para el ambiente mock, asegúrate de que api_key_or_username sea 'sandbox@siigoapi.com' "
              f"y access_key_or_secret sea la clave proporcionada.")
        return None
    
    # IMPORTANTE: Cambiar la URL al servidor mock de Apiary
    token_url = "https://private-anon-89daf21a6f-siigoapi.apiary-mock.com/auth" # <-- ¡CAMBIO AQUÍ!
    headers = {
        "Content-Type": "application/json",
        "Partner-ID": partner_id_val
    }
    data = {
        "username": username_value,
        "access_key": access_key_value,
        # En el mock, client_id y client_secret no son necesarios para la autenticación en el body
        # Sin embargo, si tu Siigo real los requiere, los dejaríamos aquí.
        # Por ahora, para el mock, el ejemplo solo usa username y access_key.
        # client_id": client_id_val,
        # client_secret": client_secret_val
    }

    try:
        response = requests.post(token_url, headers=headers, json=data)
        response.raise_for_status()
        token_data = response.json()

        update_schema = schemas_integration.IntegrationConfigTokenUpdate(
            ml_access_token=token_data.get("access_token"),
            ml_token_expires_at=datetime.now(timezone.utc) + timedelta(seconds=token_data.get("expires_in", 3600))
        )

        updated_config = crud_integration.update_integration_config(db, cast(int, config.id), config_update_data=update_schema)
        if updated_config is None:
            print(f"Advertencia: No se pudo actualizar la configuración de Siigo {config.id} en la base de datos.")
        return updated_config

    except requests.exceptions.RequestException as e:
        print(f"Error al obtener token de Siigo (mock): {e}")
        return None
    except Exception as e:
        print(f"Error inesperado al procesar token de Siigo (mock): {e}")
        return None

def is_siigo_token_expired(config: models.IntegrationConfig) -> bool:
    """
    Verifica si el token de acceso de Siigo ha expirado.
    """
    if config.ml_token_expires_at is None:
        return True

    safety_margin = timedelta(minutes=1)
    return cast(bool, datetime.now(timezone.utc) + safety_margin >= config.ml_token_expires_at)

# --- FUNCIONES DE INTERACCIÓN CON LA API DE SIIGO ---

def _get_siigo_headers(access_token: str) -> Dict[str, str]:
    """Función auxiliar para generar los headers comunes de Siigo."""
    return {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Partner-ID": settings.SIIGO_PARTNER_ID # Este sí sigue siendo tu Partner-ID real
    }

def create_siigo_invoice(access_token: str, invoice_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    # CAMBIAR ESTA URL A LA DEL MOCK SERVER PARA FACTURAS CUANDO LA ENCONTREMOS
    invoice_url = "https://api.siigo.com/v1/invoices" 
    headers = _get_siigo_headers(access_token)
    try:
        response = requests.post(invoice_url, headers=headers, json=invoice_data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error al crear factura en Siigo: {e}")
        return None

def get_siigo_products(access_token: str) -> List[Dict[str, Any]]:
    # CAMBIAR ESTA URL A LA DEL MOCK SERVER PARA PRODUCTOS CUANDO LA ENCONTREMOS
    products_url = "https://api.siigo.com/v1/products" 
    headers = _get_siigo_headers(access_token)
    try:
        response = requests.get(products_url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener productos de Siigo: {e}")
        return []

def sync_siigo_inventory(access_token: str, product_code: str, new_quantity: int) -> bool:
    # CAMBIAR ESTA URL A LA DEL MOCK SERVER PARA INVENTARIO CUANDO LA ENCONTREMOS
    inventory_update_url = f"https://api.siigo.com/v1/products/{product_code}/inventory"
    headers = _get_siigo_headers(access_token)
    data = {"quantity": new_quantity}
    try:
        response = requests.patch(inventory_update_url, headers=headers, json=data)
        response.raise_for_status()
        print(f"Sincronización de inventario para {product_code} en Siigo exitosa.")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error al sincronizar inventario de {product_code} en Siigo: {e}")
        return False