# Ubicación: /conexapi/conexapi_backend/app/services/mercadolibre.py
# Propósito: Contiene la lógica para interactuar con la API de Mercado Libre.
#            Esto incluirá funciones para autenticación (refresh de tokens),
#            obtención de productos, órdenes, etc.
# Dependencias: requests (a instalar), app.database.models, app.crud.integration

import requests
from typing import Optional, Dict, Any
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session
from app.database import models
from app.crud import integration as crud_integration
from app.config import settings # Asumo que tienes un settings.py con la configuración

# --- FUNCIONES DE AUTENTICACIÓN/REFRESH DE TOKENS ---
# Estas funciones interactuarán con la API de Mercado Libre para manejar OAuth2.

def refresh_mercadolibre_token(db: Session, config: models.IntegrationConfig) -> Optional[models.IntegrationConfig]:
    """
    Refresca el token de acceso de Mercado Libre utilizando el refresh token.
    """
    if not config.ml_refresh_token:
        print(f"Error: No refresh token found for Mercado Libre config {config.id}")
        return None

    # URL de refresh de token de Mercado Libre
    token_url = "https://api.mercadolibre.com/oauth/token"
    headers = {"Accept": "application/json", "Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "refresh_token",
        "client_id": config.api_key_or_username, # En ML, client_id es como la API key
        "client_secret": config.access_key_or_secret, # En ML, client_secret es como la secret key
        "refresh_token": config.ml_refresh_token
    }

    try:
        response = requests.post(token_url, headers=headers, data=data)
        response.raise_for_status() # Lanza una excepción para errores HTTP (4xx o 5xx)
        token_data = response.json()

        # Actualizar la configuración en la base de datos con los nuevos tokens y fecha de expiración
        config.ml_access_token = token_data["access_token"]
        config.ml_refresh_token = token_data.get("refresh_token", config.ml_refresh_token) # A veces el refresh token no cambia
        expires_in = token_data.get("expires_in", 3600) # Default a 1 hora si no se especifica
        config.ml_token_expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)

        # Usamos crud_integration para persistir los cambios
        updated_config_data = {
            "ml_access_token": config.ml_access_token,
            "ml_refresh_token": config.ml_refresh_token,
            "ml_token_expires_at": config.ml_token_expires_at
        }
        # Nota: Aquí pasamos un diccionario simple ya que crud_integration.update_integration_config
        # espera un esquema Pydantic para el update. Deberíamos crear un esquema MLTokenUpdate
        # o adaptar la función crud.
        # Por ahora, para el esqueleto, haremos un "hack" directo al objeto de la DB y luego db.commit().
        db.add(config) # Agrega el objeto modificado para que SQLAlchemy lo detecte
        db.commit()
        db.refresh(config)
        return config

    except requests.exceptions.RequestException as e:
        print(f"Error al refrescar token de Mercado Libre: {e}")
        return None
    except Exception as e:
        print(f"Error inesperado al procesar refresh token de Mercado Libre: {e}")
        return None

def is_mercadolibre_token_expired(config: models.IntegrationConfig) -> bool:
    """
    Verifica si el token de acceso de Mercado Libre ha expirado o está a punto de expirar.
    Considera expirado si falta menos de 5 minutos para la expiración.
    """
    if not config.ml_token_expires_at:
        return True # Si no hay fecha de expiración, asumimos que está expirado/no inicializado

    # Comparamos la fecha de expiración con la hora actual UTC menos un margen de seguridad
    safety_margin = timedelta(minutes=5)
    return datetime.now(timezone.utc) + safety_margin >= config.ml_token_expires_at

# --- FUNCIONES DE INTERACCIÓN CON LA API DE MERCADO LIBRE (PLACEHOLDERS) ---

def get_mercadolibre_user_info(access_token: str) -> Optional[Dict[str, Any]]:
    """
    Obtiene información básica del usuario de Mercado Libre.
    Esta es una buena función para probar la conexión.
    """
    user_info_url = "https://api.mercadolibre.com/users/me"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }
    try:
        response = requests.get(user_info_url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener info de usuario de Mercado Libre: {e}")
        return None

def get_mercadolibre_orders(access_token: str, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
    """
    Obtiene órdenes de venta de Mercado Libre.
    Por ahora, devuelve datos de ejemplo.
    """
    print("Obteniendo órdenes de Mercado Libre (simulado)...")
    # En una implementación real, aquí iría la llamada a la API de ML para obtener órdenes.
    # Por ejemplo: https://api.mercadolibre.com/orders/search
    return [
        {"id": "ML123456789", "status": "paid", "total_amount": 100.50, "items": [{"item_id": "ITEM1", "quantity": 1}]},
        {"id": "ML987654321", "status": "pending", "total_amount": 25.00, "items": [{"item_id": "ITEM2", "quantity": 2}]},
    ]

def send_mercadolibre_product_update(access_token: str, product_id: str, data: Dict[str, Any]) -> bool:
    """
    Envía una actualización de producto a Mercado Libre.
    Por ahora, solo simula el envío.
    """
    print(f"Enviando actualización de producto {product_id} a Mercado Libre (simulado)... Datos: {data}")
    # Aquí iría la llamada a la API de ML para actualizar un producto.
    return True