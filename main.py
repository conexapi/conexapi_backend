from fastapi import FastAPI
#from app.routes import oauth
from fastapi.responses import RedirectResponse

from fastapi import Request
import httpx

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

from app.api.routes import oauth
from app.db.session import get_async_session

import os

# Carga variables de entorno
load_dotenv()

# Conexión ANTIGUA a PostgreSQL usando variables de entorno
#DATABASE_URL = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"

# Conexión NUEVA a PostgreSQL usando variables de entorno
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI()
from app.api.routes import ml  # Importa el nuevo archivo ml.py
app.include_router(ml.router, prefix="/api", tags=["MercadoLibre"])
app.include_router(oauth.router, prefix="/api", tags=["OAuth"])

@app.get("/")
def read_root():
    return {"message": "¡Conexión segura a PostgreSQL con variables de entorno!"}

#2. Generar URL de Autorización: Crea un endpoint en FastAPI que redirija al usuario a la URL de autorización de MercadoLibre:
#Incorpora correctamente el endpoint /auth/ml para redirigir al usuario a la URL de autorización de MercadoLibre, utilizando las variables de entorno CLIENT_ID y REDIRECT_URI. Esto es esencial para iniciar el flujo de autenticación OAuth2.

CLIENT_ID = os.getenv("CLIENT_ID")
REDIRECT_URI = os.getenv("REDIRECT_URI")

@app.get("/auth/ml")
def auth_ml():
    auth_url = (
        f"https://auth.mercadolibre.com.co/authorization"
        f"?response_type=code"
        f"&client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
    )
    return RedirectResponse(auth_url)


#3. Intercambiar Código por Tokens: Crea un endpoint que reciba el código de autorización y lo intercambie por un access_token y un refresh_token:
#
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

@app.get("/auth/ml/callback")
async def ml_callback(request: Request):
    code = request.query_params.get("code")
    if not code:
        return {"error": "No code provided"}

    token_url = "https://api.mercadolibre.com/oauth/token"
    data = {
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "redirect_uri": REDIRECT_URI,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(token_url, data=data)
        if response.status_code != 200:
            return {"error": "Failed to obtain tokens", "details": response.text}
        tokens = response.json()
        # Aquí deberías guardar tokens["access_token"] y tokens["refresh_token"] de forma segura
        return tokens


#4. Renovar el Access Token:
# Cuando el access_token expire (después de 6 horas), utiliza el refresh_token para obtener uno nuevo:
    async def refresh_access_token(refresh_token: str):
        token_url = "https://api.mercadolibre.com/oauth/token"
        data = {
            "grant_type": "refresh_token",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "refresh_token": refresh_token,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(token_url, data=data)
            if response.status_code != 200:
                return {"error": "Failed to refresh token", "details": response.text}
            new_tokens = response.json()
            # Actualiza los tokens almacenados con new_tokens["access_token"] y new_tokens["refresh_token"]
            return new_tokens
