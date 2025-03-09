# backend/src/routes/websocket.py

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List

# Crear un router para WebSockets
router = APIRouter(prefix="/ws", tags=["websockets"])

# Lista de clientes conectados
active_connections: List[WebSocket] = []

# WebSocket para enviar alertas en tiempo real
@router.websocket("/alerts")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()  # Aceptar la conexión
    active_connections.append(websocket)  # Agregar cliente a la lista
    print("- Cliente conectado al WebSocket.")

    try:
        while True:
            await websocket.receive_text()  # Mantener la conexión activa
    except WebSocketDisconnect:
        try:
            active_connections.remove(websocket)  # Intentar eliminar cliente desconectado
            print("❌ Cliente desconectado del WebSocket.")
        except ValueError:
            print("- Intento de eliminar un cliente WebSocket que ya no existía.")

# Función para enviar alertas a todos los clientes conectados
async def send_alert_to_clients(alert_data: dict):
    for connection in active_connections:
        try:
            await connection.send_json(alert_data)  # Enviar datos en formato JSON
        except:
            try:
                active_connections.remove(connection)  # Si hay error, eliminar cliente
            except ValueError:
                pass  # Si ya no existe, no hacemos nada

# Función para enviar actualización de estado de ESP32 en tiempo real
async def send_esp32_status_to_clients(status_data: dict):
    for connection in active_connections:
        try:
            await connection.send_json(status_data)
        except:
            try:
                active_connections.remove(connection)
            except ValueError:
                pass
