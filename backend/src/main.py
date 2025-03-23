#backend/src/main.py

from fastapi import FastAPI                                     # Importa FastAPI para crear la aplicación web
from sqlalchemy.exc import OperationalError                      # Maneja errores de conexión a la base de datos
from fastapi.middleware.cors import CORSMiddleware               #Importo Cors para solicitudes externas




# Importaciones internas
from src.database import engine                                  # Importa el motor de la base de datos PostgreSQL
from src.models import Base                                      # Importa los modelos de la base de datos
from src.routes import alerts, websocket, esp32_nodes, logs      # Importamos rutas de la API y WebSockets
from src.routes import alerts_summary                            #Importo mi archivo de alerta resumen! 



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
app.include_router(alerts.router)            #alertas detectadas de la base de datos
app.include_router(websocket.router)
app.include_router(esp32_nodes.router)       #Estado de los nodos IoT esp32
app.include_router(logs.router)              #Logs

# Ruta de prueba para verificar que FastAPI funciona
@app.get("/")
def read_root():
    return {"message": "¡FastAPI está funcionando correctamente!"}

#Habilitación del cors
origins = [
    "http://localhost:5173",  # Frontend local
    "http://192.168.255.128:5173",  # desde otra ip
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(alerts_summary.router) # resumen de alertas reportada spor canal


