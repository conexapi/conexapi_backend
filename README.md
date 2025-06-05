# 📁 Ruta: conexapi_backend/README.md  
# 🧾 Archivo: README.md  
# 🎯 Objetivo: Documentar propósito general del backend del proyecto ConexAPI, su ejecución, dependencias básicas y entorno de trabajo.  
# 📌 Estado: Versión inicial. Contiene información mínima para iniciar el entorno de desarrollo y ejecución local.

# ConexAPI – Backend

Este backend es parte del sistema middleware **ConexAPI**, encargado de conectar y sincronizar datos entre Marketplaces (como MercadoLibre) y ERPs (como SIIGO Nube).

## 🚀 Tecnologías principales

- Python 3.11+
- FastAPI
- SQLAlchemy (modo async)
- MariaDB (modo local)
- JWT + OAuth2

## 📦 Estructura principal

conexapi_backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── marketplaces/
│   │       │   ├── mercadolibre.py
│   │       │   └── otro_marketplace.py
│   │       ├── erp/
│   │       │   ├── siigo.py
│   │       │   └── otro_erp.py
│   │       ├── users.py
│   │       └── api_router.py
│   ├── core/
│   │   ├── config.py
│   │   └── security.py
│   ├── db/
│   │   ├── base.py
│   │   ├── session.py
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── marketplace.py
│   │   │   ├── erp.py
│   │   │   └── venta.py
│   │   ├── crud/
│   │   │   ├── user.py
│   │   │   ├── marketplace.py
│   │   │   ├── erp.py
│   │   │   └── venta.py
│   │   └── migrations/
│   ├── services/
│   │   ├── marketplaces/
│   │   │   ├── mercadolibre.py
│   │   │   └── otro_marketplace.py
│   │   ├── erps/
│   │   │   ├── siigo.py
│   │   │   └── otro_erp.py
│   │   └── cost_calculator.py
│   └── main.py
├── tests/
│   ├── api/
│   ├── db/
│   └── services/
├── requirements.txt
├── .env.example
└── README.md

Comandos Iniciales


## ⚙️ Cómo correr el backend

```bash
cd conexapi_backend
uvicorn app.main:app --reload
