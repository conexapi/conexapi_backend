# Ubicación: /conexapi/conexapi_backend/app/services/mercadolibre.py

import requests
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session
from app.database import models
from app.crud import integration as crud_integration
from app.schemas import integration as schemas_integration
from app.config import settings

# --- FUNCIONES DE AUTENTICACIÓN/REFRESH DE TOKENS ---

def refresh_mercadolibre_token(db: Session, config: models.IntegrationConfig) -> Optional[models.IntegrationConfig]:
    """
    Refresca el token de acceso de Mercado Libre utilizando el refresh token.
    Utiliza las credenciales de la aplicación (app_id y secret_key) desde app.config.
    """
    refresh_token_value = config.ml_refresh_token
    if refresh_token_value is None or refresh_token_value == "":
        print(f"Error: No refresh token found or it is empty for Mercado Libre config {config.id}")
        return None

    client_id = settings.MERCADOLIBRE_APP_ID
    client_secret = settings.MERCADOLIBRE_SECRET_KEY

    token_url = "https://api.mercadolibre.com/oauth/token"
    headers = {"Accept": "application/json", "Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "refresh_token",
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token_value
    }

    try:
        response = requests.post(token_url, headers=headers, data=data)
        response.raise_for_status()
        token_data = response.json()

        update_schema = schemas_integration.IntegrationConfigTokenUpdate(
            ml_access_token=token_data["access_token"],
            ml_refresh_token=token_data.get("refresh_token", refresh_token_value),
            ml_token_expires_at=datetime.now(timezone.utc) + timedelta(seconds=token_data.get("expires_in", 3600))
        )

        # Aquí, el argumento para update_integration_config debe ser config_update_data
        updated_config = crud_integration.update_integration_config(db, config.id, config_update_data=update_schema)
        if not updated_config:
            print(f"Advertencia: No se pudo actualizar la configuración de Mercado Libre {config.id} en la base de datos.")
        return updated_config

    except requests.exceptions.RequestException as e:
        print(f"Error de conexión o API al refrescar token de Mercado Libre: {e}")
        return None
    except Exception as e:
        print(f"Error inesperado al procesar refresh token de Mercado Libre: {e}")
        return None

def is_mercadolibre_token_expired(config: models.IntegrationConfig) -> bool:
    """
    Verifica si el token de acceso de Mercado Libre ha expirado o está a punto de expirar.
    Considera expirado si falta menos de 5 minutos para la expiración.
    """
    if config.ml_token_expires_at is None:
        return True

    safety_margin = timedelta(minutes=5)
    return datetime.now(timezone.utc) + safety_margin >= config.ml_token_expires_at

# --- FUNCIONES DE INTERACCIÓN CON LA API DE MERCADO LIBRE (REALES) ---

def get_mercadolibre_user_info(access_token: str) -> Optional[Dict[str, Any]]:
    user_info_url = "https://api.mercadolibre.com/users/me"
    headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}
    try:
        response = requests.get(user_info_url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener info de usuario de Mercado Libre: {e}")
        return None

def get_mercadolibre_orders(access_token: str, seller_id: str, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
    orders_url = f"https://api.mercadolibre.com/orders/search?seller={seller_id}"
    params = {}
    if start_date:
        params["date_created.from"] = start_date.isoformat(timespec='seconds') + 'Z'
    if end_date:
        params["date_created.to"] = end_date.isoformat(timespec='seconds') + 'Z'
    headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}
    try:
        response = requests.get(orders_url, headers=headers, params=params)
        response.raise_for_status()
        return response.json().get("results", [])
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener órdenes de Mercado Libre: {e}")
        return []

def send_mercadolibre_product_update(access_token: str, product_id: str, data: Dict[str, Any]) -> bool:
    product_url = f"https://api.mercadolibre.com/items/{product_id}"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json", "Accept": "application/json"}
    try:
        response = requests.patch(product_url, headers=headers, json=data)
        response.raise_for_status()
        print(f"Actualización de producto {product_id} enviada a Mercado Libre.")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error al enviar actualización de producto {product_id} a Mercado Libre: {e}")
        return False