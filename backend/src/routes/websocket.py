# backend/src/routes/websocket.py

# -------------------- Importaciones --------------------
import asyncio                                      # Para gestionar tareas asincrónicas como WebSocket
from fastapi import APIRouter, WebSocket, WebSocketDisconnect  # Soporte WebSocket en FastAPI
from typing import List                             # Para especificar listas tipadas

# -------------------- Definición del Router --------------------
router = APIRouter(prefix="/ws", tags=["websockets"])  # Define el prefijo para las rutas WebSocket

# -------------------- Lista de Conexiones Activas --------------------
active_connections: List[WebSocket] = []  # Almacena los clientes WebSocket conectados

# -------------------- Endpoint: Conexión WebSocket --------------------
@router.websocket("/alerts")
async def websocket_endpoint(websocket: WebSocket):
    """
    Establece y mantiene una conexión WebSocket para alertas en tiempo real.
    Envia mensajes "keepalive" cada 10 segundos para mantener la conexión activa.
    """
    await websocket.accept()                    # Aceptar la conexión del cliente
    active_connections.append(websocket)        # Agregar el cliente a la lista de conexiones
    print("- Cliente conectado al WebSocket.")

    try:
        while True:
            # Enviar mensaje periódico para mantener la conexión
            await websocket.send_json({"type": "keepalive", "msg": "🫀 still alive"})
            await asyncio.sleep(10)
    except WebSocketDisconnect:
        # Manejar desconexión del cliente
        try:
            active_connections.remove(websocket)
            print("❌ Cliente desconectado del WebSocket.")
        except ValueError:
            print("- Cliente ya no existía.")

# -------------------- Función: Enviar alerta a todos los clientes --------------------
async def send_alert_to_clients(alert_data: dict):
    """
    Envía una alerta en formato JSON a todos los clientes conectados por WebSocket.
    """
    for connection in active_connections:
        try:
            await connection.send_json(alert_data)
        except:
            # Si la conexión falla, eliminarla de la lista
            try:
                active_connections.remove(connection)
            except ValueError:
                pass

# -------------------- Función: Enviar estado ESP32 a todos los clientes --------------------
async def send_esp32_status_to_clients(status_data: dict):
    """
    Envía una actualización del estado del ESP32 en formato JSON a todos los clientes conectados.
    """
    for connection in active_connections:
        try:
            await connection.send_json(status_data)
        except:
            # Eliminar conexiones caídas
            try:
                active_connections.remove(connection)
            except ValueError:
                pass
