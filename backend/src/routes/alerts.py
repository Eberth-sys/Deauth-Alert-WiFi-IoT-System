# backend/src/routes/alerts.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

# Importaciones internas
from src.database import get_db                          # Conexión a la base de datos
from src.models import Alert                             # Modelo de la tabla "alerts"
from src.schemas import AlertResponse                    # Esquema de respuesta
from src.routes.websocket import send_alert_to_clients   # Importamos la función para enviar alertas

# Crear un router para gestionar alertas
router = APIRouter(prefix="/alerts", tags=["alerts"])

# Endpoint para obtener las últimas alertas
@router.get("/", response_model=list[AlertResponse])
async def get_latest_alerts(limit: int = 10, db: Session = Depends(get_db)): # Consulto los últimos 10 eventos de la base de datos. 

    alerts = db.query(Alert).order_by(Alert.timestamp.desc()).limit(limit).all()

    # Si hay alertas en la BD, se envia 
    if alerts:
        last_alert = alerts[0]  # Última alerta recibida
        alert_data = {
            "id": last_alert.id,
            "nodo_iot": last_alert.nodo_iot,
            "spoofed_bssid": last_alert.spoofed_bssid,
            "target_mac": last_alert.target_mac,
            "bssid": last_alert.bssid,
            "canal": last_alert.canal,
            "timestamp": last_alert.timestamp.isoformat()
        }
        await send_alert_to_clients(alert_data)  # Enviar alerta en tiempo real

    return alerts
