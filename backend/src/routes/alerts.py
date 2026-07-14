# backend/src/routes/alerts.py

# -------------------- Librerías externas --------------------
from fastapi import APIRouter, Depends                         # Para definir rutas y manejar dependencias
from sqlalchemy.orm import Session                             # Para interactuar con la base de datos mediante SQLAlchemy

# -------------------- Módulos internos del proyecto --------------------
from src.database import get_db                                # Función para obtener una sesión de la base de datos
from src.models import Alert                                   # Modelo ORM de la tabla "alerts"
from src.schemas import AlertResponse                          # Esquema de salida que representa una alerta
from src.routes.websocket import send_alert_to_clients         # Función para enviar alertas por WebSocket
from src.services.auth_service import get_current_user         # Autenticación JWT de usuario (T2, SEC-02)

# -------------------- Inicialización del router --------------------
router = APIRouter(prefix="/alerts", tags=["alerts"])          # Prefijo de ruta y etiqueta de grupo para documentación

# -------------------- Ruta: Obtener las últimas alertas --------------------
@router.get("/", response_model=list[AlertResponse], dependencies=[Depends(get_current_user)])
async def get_latest_alerts(limit: int = 10, db: Session = Depends(get_db)):
    """
    Retorna las últimas 'n' alertas registradas en la base de datos.
    Además, si hay resultados, envía la alerta más reciente a todos los clientes WebSocket conectados.
    """
    alerts = db.query(Alert).order_by(Alert.timestamp.desc()).limit(limit).all()

    # Si existen alertas, se prepara y envía la más reciente en tiempo real por WebSocket
    if alerts:
        last_alert = alerts[0]
        alert_data = {
            "id": last_alert.id,
            "nodo_iot": last_alert.nodo_iot,
            "spoofed_bssid": last_alert.spoofed_bssid,
            "target_mac": last_alert.target_mac,
            "bssid": last_alert.bssid,
            "canal": last_alert.canal,
            "event_type": last_alert.event_type,           # Tipo de evento (F1, DEC-0003)
            "timestamp": last_alert.timestamp.isoformat()  # Formato ISO para facilitar compatibilidad en frontend
        }
        await send_alert_to_clients(alert_data)  # Enviar alerta a los clientes conectados

    return alerts
