import os
import psycopg2
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
env_path = os.path.join(os.path.dirname(__file__), "..", "docker", ".env")
load_dotenv(env_path)  # Se carga dinámicamente sin necesidad de rutas fijas

def get_db_connection():
    """Crea una conexión a PostgreSQL dentro del contenedor Docker."""
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("PG_DB"),          # Nombre de la base de datos
            user=os.getenv("PG_USER"),          # Usuario de la base de datos
            password=os.getenv("PG_PASSWORD"),  # Contraseña de la base de datos
            host=os.getenv("PG_HOST"),          # Dirección del servidor (localhost o el nombre del contenedor)
            port=int(os.getenv("PG_PORT", 5432)) # Convertir a entero en caso de problemas
        )
        return conn
    except psycopg2.OperationalError as e:
        print(f"[ERROR] - No se pudo conectar a PostgreSQL: {e}")
        return None
    except Exception as e:
        print(f"[ERROR] - Error desconocido en la conexión a PostgreSQL: {e}")
        return None
