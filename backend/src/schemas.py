# backend/src/schemas.py

from pydantic import BaseModel          #definir esquemas de datos
from datetime import datetime

# Esquema para recibir datos cuando se crea una nueva alerta
class AlertCreate(BaseModel):
    nodo_iot: str                       # Dispositivo que detectó el ataque
    spoofed_bssid: str                  # BSSID suplantado
    target_mac: str                     # MAC de destino del ataque
    bssid: str                          # BSSID original
    canal: int                          # Canal donde se detectó el ataque

# Esquema para enviar datos de una alerta ya creada (incluyendo timestamp e ID)
class AlertResponse(AlertCreate):             
    id: int                             # Identificador único
    timestamp: datetime                 # Fecha y hora del evento

    class Config:
        from_attributes = True          # Convierto de modelo SQLAlchemy a Pydantic automáticamente
