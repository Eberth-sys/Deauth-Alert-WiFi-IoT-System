#backend\src\routes\esp32_nodes.py

# -------------------- Importaciones --------------------
import asyncio
from datetime import datetime
from fastapi import APIRouter, Depends                         # Framework para rutas y dependencias
from sqlalchemy.orm import Session                            # Sesiones de base de datos con SQLAlchemy
from src.database import get_db                               # Conexión a la base de datos PostgreSQL
from src.models import ESP32Status                            # Modelo ORM para el estado de los nodos ESP32
from src.schemas import ESP32StatusResponse                   # Esquema de datos para validación y respuesta
from src.routes.websocket import send_esp32_status_to_clients # Función para emitir datos por WebSocket

# -------------------- Crear router --------------------
router = APIRouter(prefix="/esp32-nodes", tags=["esp32_nodes"])

# -------------------- Endpoint: Obtener estado de nodos --------------------
@router.get("/", response_model=list[ESP32StatusResponse])
def get_esp32_status(db: Session = Depends(get_db)):
    """
    Retorna una lista con el estado actual de todos los nodos ESP32 registrados.
    """
    return db.query(ESP32Status).all()

# -------------------- Endpoint: Actualizar estado desde processing-layer --------------------
@router.post("/update")
async def update_esp32_status(esp32_data: ESP32StatusResponse, db: Session = Depends(get_db)):
    """
    Recibe el estado actualizado de un nodo ESP32 y lo guarda en la base de datos.
    También emite la actualización vía WebSocket para clientes conectados.
    """
    existing_device = db.query(ESP32Status).filter(ESP32Status.device_name == esp32_data.device_name).first()

    # Usa la fecha y hora actuales si no se incluye `last_update`
    last_update = esp32_data.last_update or datetime.now()

    if existing_device:
        # Actualiza dispositivo existente
        existing_device.status = esp32_data.status
        existing_device.last_update = last_update
    else:
        # Crea un nuevo registro si el dispositivo no existe
        new_device = ESP32Status(
            device_name=esp32_data.device_name,
            mac_address=esp32_data.mac_address,
            status=esp32_data.status,
            last_update=last_update
        )
        db.add(new_device)

    db.commit()

    # Enviar actualización en tiempo real mediante WebSockets sin bloquear FastAPI
    asyncio.create_task(send_esp32_status_to_clients(esp32_data.dict()))

    return {"message": f"Estado de {esp32_data.device_name} actualizado correctamente."}
