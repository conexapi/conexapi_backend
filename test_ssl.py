import pymysql
from dotenv import load_dotenv
import os

load_dotenv()

# Configuración desde .env
config = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME'),
    'port': int(os.getenv('DB_PORT', 3306))
}

print("Probando conexión SSL...")
print(f"Host: {config['host']}")
print(f"Usuario: {config['user']}")
print(f"Base de datos: {config['database']}")
print(f"Puerto: {config['port']}")

# Rutas de certificados desde .env
ssl_ca = os.getenv('DB_SSL_CA')
ssl_cert = os.getenv('DB_SSL_CERT')
ssl_key = os.getenv('DB_SSL_KEY')

print(f"\nCertificados configurados:")
print(f"CA: {ssl_ca}")
print(f"CERT: {ssl_cert}")
print(f"KEY: {ssl_key}")

# Verificar si los archivos existen
print(f"\nVerificando archivos:")
print(f"CA existe: {os.path.exists(ssl_ca) if ssl_ca else 'No configurado'}")
print(f"CERT existe: {os.path.exists(ssl_cert) if ssl_cert else 'No configurado'}")
print(f"KEY existe: {os.path.exists(ssl_key) if ssl_key else 'No configurado'}")

try:
    # Intentar conexión con SSL
    connection = pymysql.connect(
        **config,
        ssl_ca=ssl_ca,
        ssl_cert=ssl_cert,
        ssl_key=ssl_key
    )
    
    with connection.cursor() as cursor:
        cursor.execute("SHOW STATUS LIKE 'Ssl_cipher'")
        result = cursor.fetchone()
        print(f"\n✅ Conexión SSL exitosa!")
        print(f"Cipher: {result[1] if result else 'No disponible'}")
        
except Exception as e:
    print(f"\n❌ Error de conexión: {e}")
    
    # Intentar sin certificados específicos (solo SSL básico)
    try:
        print("\nIntentando con SSL básico...")
        connection = pymysql.connect(
            **config,
            ssl={}  # SSL básico sin certificados específicos
        )
        print("✅ Conexión SSL básica exitosa!")
        connection.close()
    except Exception as e2:
        print(f"❌ Error con SSL básico: {e2}")