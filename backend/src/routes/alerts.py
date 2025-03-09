# backend/src/routes/alerts.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.database import get_db                            # Conexión a la base de datos
from src.models import Alert                               # Modelo de la tabla "alerts"
from src.schemas import AlertResponse                      # Esquema de respuesta

# Crear un router para gestionar alertas
router = APIRouter(prefix="/alerts", tags=["alerts"])

@router.get("/", response_model=list[AlertResponse])
def get_latest_alerts(limit: int = 10, db: Session = Depends(get_db)): # Consulto los últimos 10 eventos de la base de datos. 
    
    alerts = db.query(Alert).order_by(Alert.timestamp.desc()).limit(limit).all()
    return alerts
