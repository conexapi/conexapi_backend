import mysql.connector
import ssl
from mysql.connector import Error

def test_mysql_connection():
    connection = None
    cursor = None
    
    try:
        # Conexión a MySQL (sin SSL por compatibilidad)
        connection = mysql.connector.connect(
            host='127.0.0.1',
            database='test_conexapi',
            user='root',  # ajustar según tu usuario
            password='DevMySQL2025#',  # CAMBIAR POR TU PASSWORD REAL
            auth_plugin='mysql_native_password',
            autocommit=True
        )
        
        if connection.is_connected():
            print("✅ CONEXIÓN A MYSQL EXITOSA")
            
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM usuarios_test")
            records = cursor.fetchall()
            
            # Verificación segura de records
            if records is not None:
                print(f"📊 Registros encontrados: {len(records)}")
                for row in records:
                    print(f"   ID: {row[0]}, Nombre: {row[1]}, Email: {row[2]}")
            else:
                print("📊 No se encontraron registros")
                
        else:
            print("❌ NO SE PUDO CONECTAR A MYSQL")
            
    except Error as e:
        print(f"❌ ERROR DE CONEXIÓN MYSQL: {e}")
    except Exception as e:
        print(f"❌ ERROR GENERAL: {e}")
    finally:
        # Cerrar conexiones de forma segura
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()
            print("🔒 Conexión cerrada")

if __name__ == "__main__":
    print("🧪 INICIANDO PRUEBA DE CONEXIÓN MYSQL CON SSL...")
    test_mysql_connection()
    print("🏁 PRUEBA COMPLETADA")