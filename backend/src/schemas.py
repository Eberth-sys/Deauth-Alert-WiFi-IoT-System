# backend/src/schemas.py

from pydantic import BaseModel          # Define modelos de datos con validación automática
from datetime import datetime           # Permite manejar fechas y horas
from pydantic import EmailStr           # Valida que un campo sea un email válido


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

# Esquema para respuestas sobre el estado de los ESP32
class ESP32StatusResponse(BaseModel):
    device_name: str
    mac_address: str
    status: str
    last_update: datetime

    class Config:
        from_attributes = True

# Para registro
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

# Para login
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Para respuestas públicas (sin password)
class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_admin: bool
    created_at: datetime

    class Config:
        from_attributes = True  # Para convertir desde SQLAlchemy directamente