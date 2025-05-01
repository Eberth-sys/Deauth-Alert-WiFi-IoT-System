#backend/src/main.py
# backend/src/main.py

# backend/src/main.py

# -------------------- Librerías externas --------------------
from fastapi import FastAPI                                # Framework principal para construir la API
from sqlalchemy.exc import OperationalError                # Manejo de errores al conectar con la base de datos
from fastapi.middleware.cors import CORSMiddleware         # Middleware para permitir solicitudes desde otros orígenes (CORS)
from fastapi.security import OAuth2PasswordBearer          # Esquema de seguridad para autenticación con JWT
from fastapi.openapi.utils import get_openapi              # Permite personalizar la documentación de Swagger/OpenAPI

# -------------------- Módulos internos del proyecto --------------------
from src.database import engine                                        # Motor de conexión a la base de datos PostgreSQL
from src.models import Base                                            # Base declarativa para crear las tablas de los modelos
from src.routes import alerts, websocket, esp32_nodes, logs            # Rutas principales de la API
from src.routes import alerts_summary, custom_queries, auth            # Rutas adicionales: resúmenes, consultas personalizadas y autenticación
from src.routes import admin_routes                                    # Importa las rutas exclusivas para administradores



# -------------------- Instancia principal --------------------
app = FastAPI()                                            # Crea la instancia principal de FastAPI

# -------------------- Seguridad Swagger UI (JWT ) --------------------
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")  # Configura el esquema de seguridad OAuth2 con JWT

# Personaliza la documentación para incluir autenticación JWT
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Sistema IoT WiFi",
        version="1.0.0",
        description="Monitoreo y autenticación en redes Wi-Fi",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path]:
            openapi_schema["paths"][path][method]["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi   # Aplica la personalización a Swagger UI

# -------------------- Eventos --------------------
@app.on_event("startup")
def startup():
    try:
        with engine.connect() as connection:
            print("✅ Conexión a PostgreSQL exitosa.")
        Base.metadata.create_all(bind=engine)                     # Crea las tablas si no existen
        print("✅ Tablas creadas en PostgreSQL correctamente.")
    except OperationalError as e:
        print(f"❌ Error al conectar con la base de datos: {e}")

# -------------------- Middleware CORS --------------------
origins = [
    "http://localhost:5173",           # Frontend local
    "http://192.168.255.132:5173",     # IP local del desarrollador
    "http://192.168.255.100:5173"      # Otra IP permitida
]

# Configuración del middleware para permitir solicitudes desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            # Lista de orígenes permitidos
    allow_credentials=True,
    allow_methods=["*"],              # Permitir todos los métodos (GET, POST, etc.)
    allow_headers=["*"],              # Permitir todos los encabezados
)

# -------------------- Incluir rutas --------------------
app.include_router(alerts.router)             # Rutas para alertas
app.include_router(websocket.router)          # Rutas WebSocket en tiempo real
app.include_router(esp32_nodes.router)        # Rutas para gestión de nodos ESP32
app.include_router(logs.router)               # Rutas para logs BLE
app.include_router(alerts_summary.router)     # Rutas para resumen de alertas
app.include_router(custom_queries.router)     # Rutas para consultas personalizadas
app.include_router(auth.router)               # Rutas de autenticación (login, registro)
app.include_router(admin_routes.router)       # Agrega esas rutas a la aplicación principal FastAPI bajo el prefijo /admin

# -------------------- Ruta base --------------------
@app.get("/")
def read_root():
    return {"message": "¡FastAPI está funcionando correctamente!"}  # Respuesta por defecto para probar la API
