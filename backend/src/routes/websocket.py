# backend/src/routes/websocket.py

import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List

# Crear un router para WebSockets
router = APIRouter(prefix="/ws", tags=["websockets"])

# Lista de clientes conectados
active_connections: List[WebSocket] = []

# WebSocket para enviar alertas en tiempo real
@router.websocket("/alerts")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    print("- Cliente conectado al WebSocket.")

    try:
        while True:
            await websocket.send_json({"type": "keepalive", "msg": "🫀 still alive"})
            await asyncio.sleep(10)  # cada 10 segundos
    except WebSocketDisconnect:
        try:
            active_connections.remove(websocket)
            print("❌ Cliente desconectado del WebSocket.")
        except ValueError:
            print("- Cliente ya no existía.")

# Función para enviar alertas a todos los clientes conectados
async def send_alert_to_clients(alert_data: dict):
    for connection in active_connections:
        try:
            await connection.send_json(alert_data)
        except:
            try:
                active_connections.remove(connection)
            except ValueError:
                pass

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
