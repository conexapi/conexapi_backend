# 📁 Ruta: conexapi_backend/docs/CONEXAPI_STACK.md  
# 🧾 Archivo: CONEXAPI_STACK.md  
# 🎯 Objetivo: Documentar las tecnologías oficiales utilizadas en ConexAPI backend, su propósito y justificación.  
# 📌 Estado: Inicial. Resume las tecnologías ya validadas y adoptadas para el backend.

# 🧱 ConexAPI – Stack Tecnológico (Backend)

Este documento describe el stack tecnológico aprobado para el backend del sistema middleware **ConexAPI**, encargado de conectar y sincronizar ventas entre Marketplaces y ERPs.

---

## 🚀 Lenguaje y Framework

| Tecnología | Versión | Rol |
|------------|---------|-----|
| Python     | 3.11+   | Lenguaje principal del backend |
| FastAPI    | 0.104.1 | Framework web asincrónico (API REST) |
| Uvicorn    | 0.24.0  | Servidor ASGI para FastAPI |

---

## 🗄️ Base de Datos

| Tecnología | Uso |
|------------|-----|
| MariaDB / MySQL | Almacenamiento principal (modo desarrollo y producción) |
| SQLAlchemy (async) | ORM moderno y escalable |
| aiomysql | Cliente async compatible con SQLAlchemy 2.0 |

---

## 🔐 Seguridad

| Tecnología | Uso |
|------------|-----|
| python-jose | Firmado y verificación de tokens JWT |
| OAuth2 | Flujo seguro de autorización (ML y SIIGO) |
| passlib + bcrypt | Hasheo de contraseñas |
| python-multipart | Manejo de formularios y archivos |

---

## 🌍 Comunicación con APIs externas

| Tecnología | Uso |
|------------|-----|
| httpx | Cliente HTTP async |
| requests | Cliente HTTP clásico (respaldo) |

---

## ⚙️ Utilidades y Configuración

| Tecnología | Uso |
|------------|-----|
| pydantic-settings | Configuración basada en variables de entorno |
| python-dotenv | Carga de `.env` |
| structlog | Logging estructurado |
| alembic | Migraciones de BD |

---

## 🧪 Testing y Calidad

| Tecnología | Uso |
|------------|-----|
| pytest, pytest-asyncio, pytest-cov | Testing |
| black, isort, flake8, mypy | Calidad de código |

---

## 🚀 Despliegue y CI

| Tecnología | Uso |
|------------|-----|
| gunicorn | Servidor productivo (opcional) |
| GitHub Actions | CI/CD adaptable |
