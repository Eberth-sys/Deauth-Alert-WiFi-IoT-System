#backend/src/main.py

from fastapi import FastAPI                      # Importa FastAPI para crear la aplicación web
from sqlalchemy.exc import OperationalError      # Maneja errores de conexión a la base de datos

# Importaciones internas
from src.database import engine                  # Importa el motor de la base de datos PostgreSQL
from src.models import Base                      # Importa los modelos de la base de datos
from src.routes import alerts, websocket, esp32_nodes  # Importamos rutas de la API y WebSockets

# Instancia de FastAPI
app = FastAPI()

# Crear tablas al iniciar la aplicación
@app.on_event("startup")
def startup():
    try:
        with engine.connect() as connection:
            print("✅ Conexión a PostgreSQL exitosa.")

        Base.metadata.create_all(bind=engine)  # Crear la tabla en PostgreSQL si no existe
        print("✅ Tablas creadas en PostgreSQL correctamente.")
    except OperationalError as e:
        print(f"❌ Error al conectar con la base de datos: {e}")

# Incluir las rutas en FastAPI
app.include_router(alerts.router)
app.include_router(websocket.router)
app.include_router(esp32_nodes.router)

# Ruta de prueba para verificar que FastAPI funciona
@app.get("/")
def read_root():
    return {"message": "¡FastAPI está funcionando correctamente!"}
