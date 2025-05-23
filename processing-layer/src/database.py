#/src/datebase.py

# -------------------- Importaciones --------------------
import os                                   # Para acceder a las variables de entorno
import psycopg2                             # Librería para conectar con bases de datos PostgreSQL
from dotenv import load_dotenv              # Para cargar las variables de entorno desde un archivo .env

# -------------------- Cargar archivo .env --------------------
env_path = os.path.join(os.path.dirname(__file__), "..", "docker", ".env")  # Ruta relativa al archivo .env
load_dotenv(env_path)  # Cargar variables de entorno desde el archivo especificado

# -------------------- Función: Obtener conexión con PostgreSQL --------------------
def get_db_connection():
    """Crea una conexión a PostgreSQL dentro del contenedor Docker."""
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("PG_DB"),           # Nombre de la base de datos (desde .env)
            user=os.getenv("PG_USER"),           # Usuario de la base de datos
            password=os.getenv("PG_PASSWORD"),   # Contraseña del usuario
            host=os.getenv("PG_HOST"),           # Dirección del servidor (host)
            port=int(os.getenv("PG_PORT", 5432)) # Puerto del servidor (con valor por defecto 5432)
        )
        return conn  # Retorna la conexión si es exitosa
    except psycopg2.OperationalError as e:
        print(f"[ERROR] - No se pudo conectar a PostgreSQL: {e}")  # Error específico de conexión
        return None
    except Exception as e:
        print(f"[ERROR] - Error desconocido en la conexión a PostgreSQL: {e}")  # Otros errores
        return None

