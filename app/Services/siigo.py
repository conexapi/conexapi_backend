# Ubicación: /conexapi/conexapi_backend/app/services/siigo.py
# Propósito: Contiene las funciones de servicio para interactuar con la API de Siigo,
#            incluyendo la obtención de tokens y la manipulación de documentos y productos.
# Dependencias: requests, sqlalchemy.orm.Session, app.database.models, app.crud.integration,
#               app.schemas.integration, app.config

import requests
from typing import Optional, Dict, Any, List, cast # Asegúrate de que 'cast' está importado
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session
from app.database import models
from app.crud import integration as crud_integration
from app.schemas import integration as schemas_integration
from app.config import settings # Importamos settings para acceder a las URLs de la configuración

# --- FUNCIONES DE UTILIDAD PARA TOKENS ---

def is_siigo_token_expired(config: models.IntegrationConfig) -> bool:
    """
    Verifica si el token de acceso de Siigo almacenado ha expirado.
    Considera un pequeño margen de seguridad antes de la expiración real.
    """
    # Usamos ml_token_expires_at para el token de Siigo también
    # Solución para Linea 25: Comprobar directamente si los valores son None.
    # El objeto `config` es una instancia de `models.IntegrationConfig` cargada de la DB,
    # por lo que sus atributos `ml_token_expires_at` y `ml_access_token` ya son los valores de Python.
    if config.ml_token_expires_at is None or config.ml_access_token is None:
        # Si no hay fecha de expiración o no hay token, asumimos que está expirado o no se ha obtenido.
        return True

    # Solución para Linea 38: Usar `cast` para decirle a Pylance que `refresh_interval_minutes` es un `int`.
    # Aunque el modelo ya tiene un default y no es nullable, Pylance a veces es muy estricto.
    safety_margin_minutes: int = cast(int, config.refresh_interval_minutes) 
    safety_margin = timedelta(minutes=safety_margin_minutes)
    
    # Obtener la hora actual en UTC para comparar
    now_utc = datetime.now(timezone.utc)
    
    # Solución para Linea 48: Esta era una consecuencia de la línea 38.
    # Al asegurar que `safety_margin_minutes` es `int`, la operación `timedelta`
    # y la suma con `now_utc` producirán tipos de Python correctos.
    # `config.ml_token_expires_at` es un `datetime` (o ya lo comprobamos como None).
    # Por lo tanto, la comparación debería resultar en un `bool` sin problemas.
     return cast(bool, config.ml_token_expires_at <= (now_utc + safety_margin)) # type: ignore


# --- FUNCIONES DE AUTENTICACIÓN/OBTENCIÓN DE TOKENS PARA SIIGO ---

def get_siigo_token(db: Session, config: models.IntegrationConfig) -> Optional[models.IntegrationConfig]:
    """
    Obtiene un token de acceso para Siigo Cloud y lo guarda en la base de datos.
    Utiliza las credenciales de la aplicación (client_id y client_secret) desde app.config
    y las credenciales de la cuenta del cliente (username y access_key) desde la config.
    """
    client_id_val = settings.SIIGO_CLIENT_ID
    client_secret_val = settings.SIIGO_CLIENT_SECRET

    username_value = config.api_key_or_username
    access_key_value = config.access_key_or_secret

    if (username_value is None or cast(str, username_value) == "" or
        access_key_value is None or cast(str, access_key_value) == ""):
        print(f"Error: Username o Access Key incompletos o vacíos para Siigo config {config.id}")
        return None

    token_url = f"{settings.SIIGO_AUTH_URL}/connect/token"

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
        "Partner-Id": settings.SIIGO_PARTNER_ID
    }
    data = {
        "client_id": client_id_val,
        "client_secret": client_secret_val,
        "scope": "offline_access",
        "grant_type": "password",
        "username": username_value,
        "password": access_key_value,
    }

    # Solución para "response" is possibly unbound: Inicializar `response` antes del bloque try.
    response: Optional[requests.Response] = None # Inicializar response como None

    try:
        response = requests.post(token_url, headers=headers, data=data)
        response.raise_for_status()
        token_data = response.json()

        access_token = token_data.get("access_token")
        expires_in = token_data.get("expires_in") # Segundos hasta la expiración
        refresh_token = token_data.get("refresh_token") # Si Siigo lo proporciona

        if not access_token:
            print(f"Error al obtener token de Siigo: No se recibió access_token en la respuesta. Respuesta: {token_data}")
            return None

        # Calcular la fecha de expiración en UTC
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)

        # Actualizar la configuración de la integración en la base de datos
        # No actualizamos refresh_interval_minutes aquí, ya que es un valor configurable por el usuario, no por la API de Siigo
        update_data = schemas_integration.IntegrationConfigTokenUpdate(
            ml_access_token=access_token, # Usamos ml_access_token para guardar el token de Siigo
            ml_refresh_token=refresh_token, # Usamos ml_refresh_token para guardar el refresh token de Siigo
            ml_token_expires_at=expires_at # Guardamos la fecha de expiración
        )
        
        # Confirmación de la línea 118: Sí, está perfecto con `cast(int, config.id)`.
        # Esto le dice a Pylance que `config.id` es un `int` en tiempo de ejecución.
        updated_config = crud_integration.update_integration_config(
            db=db,
            config_id=cast(int, config.id), # Castear a int para Pylance
            config_update_data=update_data
        )
        if updated_config is None:
            print(f"Error: No se pudo actualizar la configuración de Siigo en DB para config ID {config.id}")
            return None

        print(f"Token de Siigo obtenido y guardado exitosamente para config ID {config.id}. Expira en {expires_in} segundos.")
        return updated_config

    except requests.exceptions.HTTPError as http_err:
        # Asegurar que 'response' se comprueba si no es None antes de intentar acceder a .text
        response_text = response.text if response is not None else 'N/A'
        print(f"Error HTTP al obtener token de Siigo para config ID {config.id}: {http_err}. Respuesta: {response_text}")
        return None
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Error de conexión al obtener token de Siigo para config ID {config.id}: {conn_err}")
        return None
    except requests.exceptions.Timeout as timeout_err:
        print(f"Tiempo de espera agotado al obtener token de Siigo para config ID {config.id}: {timeout_err}")
        return None
    except requests.exceptions.RequestException as req_err:
        print(f"Error general al obtener token de Siigo para config ID {config.id}: {req_err}")
        return None
    except Exception as e:
        print(f"Error inesperado al obtener token de Siigo para config ID {config.id}: {e}")
        return None

def _get_siigo_headers(access_token: str) -> Dict[str, str]:
    """
    Función interna para construir las cabeceras de autorización para las llamadas a la API de Siigo.
    Asegura que 'Partner-Id' esté siempre presente.
    """
    return {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "Partner-Id": settings.SIIGO_PARTNER_ID
    }

def create_siigo_invoice(access_token: str, invoice_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    # Usamos la URL base de la API definida en settings
    invoice_url = f"{settings.SIIGO_API_BASE_URL}/invoices"
    headers = _get_siigo_headers(access_token)
    try:
        response = requests.post(invoice_url, headers=headers, json=invoice_data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error al crear factura en Siigo: {e}")
        return None

def get_siigo_products(access_token: str) -> List[Dict[str, Any]]:
    # Usamos la URL base de la API definida en settings
    products_url = f"{settings.SIIGO_API_BASE_URL}/products"
    headers = _get_siigo_headers(access_token)
    try:
        response = requests.get(products_url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener productos de Siigo: {e}")
        return []

def sync_siigo_inventory(access_token: str, product_code: str, new_quantity: int) -> bool:
    # Usamos la URL base de la API definida en settings
    inventory_update_url = f"{settings.SIIGO_API_BASE_URL}/products/{product_code}/inventory"
    headers = _get_siigo_headers(access_token)
    data = {"quantity": new_quantity}
    try:
        response = requests.patch(inventory_update_url, headers=headers, json=data)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error al actualizar inventario en Siigo: {e}")
        return False