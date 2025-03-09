#backend/src/database.py

import os                                                  # Acceder a variables de entorno del SO
from sqlalchemy import create_engine                       # Crea la conexión con la base de datos
from sqlalchemy.orm import sessionmaker, declarative_base  # Maneja sesiones y modelos ORM
from dotenv import load_dotenv                             # Carga variables de entorno desde un archivo .env


# Cargar variables de entorno desde .env
load_dotenv()

# Configuración de la conexión a PostgreSQL
DATABASE_URL = f"postgresql://{os.getenv('PG_USER')}:{os.getenv('PG_PASSWORD')}@{os.getenv('PG_HOST')}:{os.getenv('PG_PORT')}/{os.getenv('PG_DB')}"

# Crear el motor de la base de datos
engine = create_engine(DATABASE_URL)

# Crear una sesión
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para modelos de SQLAlchemy
Base = declarative_base()

# Función para obtener una sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
