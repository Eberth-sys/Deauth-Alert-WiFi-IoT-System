# backend/src/database.py

# -------------------- Importaciones estándar y externas --------------------
import os                                                  # Para acceder a variables de entorno del sistema operativo
from sqlalchemy import create_engine                       # Para crear la conexión con la base de datos PostgreSQL
from sqlalchemy.orm import sessionmaker, declarative_base  # Para manejar sesiones y definir modelos ORM
from dotenv import load_dotenv                             # Para cargar variables de entorno desde un archivo .env

# -------------------- Cargar variables de entorno --------------------
load_dotenv()  # Esto permite que las variables definidas en .env estén disponibles con os.getenv

# -------------------- Configuración de la base de datos --------------------
# Armamos la URL de conexión usando variables de entorno (.env)
DATABASE_URL = f"postgresql://{os.getenv('PG_USER')}:{os.getenv('PG_PASSWORD')}@{os.getenv('PG_HOST')}:{os.getenv('PG_PORT')}/{os.getenv('PG_DB')}"

# -------------------- Inicialización de componentes de SQLAlchemy --------------------
# Creamos el motor de conexión usando la URL
engine = create_engine(DATABASE_URL)

# Creamos la fábrica de sesiones para interactuar con la base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declaramos la base desde la cual se extienden los modelos
Base = declarative_base()

# -------------------- Función para obtener sesión de base de datos --------------------
def get_db():
    """
    Proporciona una sesión de base de datos a las rutas que lo necesiten.
    Se asegura de cerrarla una vez usada.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
