# backend/src/routes/websocket.py

# -------------------- Importaciones --------------------
import asyncio                                      # Para gestionar tareas asincrónicas como WebSocket
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends  # Soporte WebSocket en FastAPI
from sqlalchemy.orm import Session                  # Sesión de base de datos para validar el token
from typing import List                             # Para especificar listas tipadas

from src.database import get_db                                # Sesión de BD para validar el token
from src.services.auth_service import get_user_from_token      # Validación JWT del handshake (SEC-04)

# -------------------- Definición del Router --------------------
router = APIRouter(prefix="/ws", tags=["websockets"])  # Define el prefijo para las rutas WebSocket

# -------------------- Lista de Conexiones Activas --------------------
active_connections: List[WebSocket] = []  # Almacena los clientes WebSocket conectados

# -------------------- Endpoint: Conexión WebSocket --------------------
@router.websocket("/alerts")
async def websocket_endpoint(websocket: WebSocket, db: Session = Depends(get_db)):
    """
    Establece y mantiene una conexión WebSocket para alertas en tiempo real.
    Envia mensajes "keepalive" cada 10 segundos para mantener la conexión activa.

    Autenticación (SEC-04): el token JWT viaja por query param (?token=...) porque
    los WebSocket del navegador no permiten header Authorization. En producción
    usar WSS para cifrar el query en tránsito. Si el token falta o es inválido,
    se rechaza el handshake con close code 1008 (Policy Violation) antes de accept().
    """
    token = websocket.query_params.get("token")     # Token JWT enviado en la query
    user = get_user_from_token(token, db)           # Valida firma/expiración y existencia del usuario
    if user is None:
        await websocket.close(code=1008)            # Rechazo por autenticación (antes de aceptar)
        return

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
