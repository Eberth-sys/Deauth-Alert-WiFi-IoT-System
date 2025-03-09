# backend/src/routes/websocket.py

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List

# Crear un router para WebSockets
router = APIRouter(prefix="/ws", tags=["websockets"])

# Lista de clientes conectados
active_connections: List[WebSocket] = []

# WebSocket para enviar alertas en tiempo real
@router.websocket("/alerts")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()                       # Aceptar la conexión
    active_connections.append(websocket)           # Agregar cliente a la lista
    print("🔌 Cliente conectado al WebSocket.")

    try:
        while True:
            await websocket.receive_text()        # Mantener la conexión activa
    except WebSocketDisconnect:
        active_connections.remove(websocket)  # Eliminar cliente desconectado
        print("❌ Cliente desconectado del WebSocket.")

# Función para enviar alertas a todos los clientes conectados
async def send_alert_to_clients(alert_data: dict):
    for connection in active_connections:          # Recorre todos los clientes conectados
        try:
            await connection.send_json(alert_data)  # Enviar datos en formato JSON
        except:
            active_connections.remove(connection)  # Si hay error, eliminar cliente
