#backend\src\routes\esp32_nodes.py

import asyncio
from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.database import get_db                                # Conexión a la base de datos
from src.models import ESP32Status                             # Modelo de la tabla "esp32_status"
from src.schemas import ESP32StatusResponse                    # Esquema de respuesta
from src.routes.websocket import send_esp32_status_to_clients  # Enviamos WebSockets desde el backend

# Crear un router para manejar el estado de los ESP32
router = APIRouter(prefix="/esp32-nodes", tags=["esp32_nodes"])

# Endpoint para obtener el estado de todos los ESP32
@router.get("/", response_model=list[ESP32StatusResponse])
def get_esp32_status(db: Session = Depends(get_db)):
    """
    Obtiene el estado actual de todos los ESP32 registrados en la base de datos.
    """
    return db.query(ESP32Status).all()

# Endpoint para recibir actualizaciones de estado desde processing-layer
@router.post("/update")
async def update_esp32_status(esp32_data: ESP32StatusResponse, db: Session = Depends(get_db)):
    """
    Recibe actualizaciones de estado de los ESP32 desde processing-layer y envía WebSocket.
    """
    existing_device = db.query(ESP32Status).filter(ESP32Status.device_name == esp32_data.device_name).first()

    # Usamos la fecha actual si `last_update` no está en la solicitud
    last_update = esp32_data.last_update or datetime.now()

    if existing_device:
        existing_device.status = esp32_data.status
        existing_device.last_update = last_update
    else:
        new_device = ESP32Status(
            device_name=esp32_data.device_name,
            mac_address=esp32_data.mac_address,
            status=esp32_data.status,
            last_update=last_update
        )
        db.add(new_device)

    db.commit()

    # Enviar actualización en tiempo real por WebSockets SIN BLOQUEAR FastAPI
    asyncio.create_task(send_esp32_status_to_clients(esp32_data.dict()))

    return {"message": f"Estado de {esp32_data.device_name} actualizado correctamente."}
