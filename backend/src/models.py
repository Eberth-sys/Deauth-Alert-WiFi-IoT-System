# backend/src/models.py

# -------------------- Librerías externas --------------------
from sqlalchemy import Column, Integer, String, TIMESTAMP, CheckConstraint  # Tipos de columnas y restricciones
from sqlalchemy.sql import func                                             # Para usar funciones SQL como now()
from src.database import Base                                               # Importa la base declarativa desde database.py
from sqlalchemy import Boolean                                              # Tipo de dato booleano

# -------------------- Modelo: Alertas --------------------
class Alert(Base):
    __tablename__ = "alerts"  # Nombre de la tabla en PostgreSQL

    id = Column(Integer, primary_key=True, index=True, nullable=False)  # ID único
    nodo_iot = Column(String, nullable=False)                           # Nodo IoT que detectó la alerta
    spoofed_bssid = Column(String(17), nullable=False)                  # BSSID falsificado
    target_mac = Column(String(17), nullable=False)                     # MAC objetivo del ataque
    bssid = Column(String(17), nullable=False)                          # BSSID legítimo
    canal = Column(Integer, nullable=False)                             # Canal en que se detectó el ataque
    event_type = Column(String(16), nullable=False, server_default="'deauth'")  # Tipo de evento 802.11 (deauth/disassoc) — F1, DEC-0003
    timestamp = Column(TIMESTAMP, server_default=func.now())            # Fecha y hora del evento

# -------------------- Modelo: Estado de nodos ESP32 --------------------
class ESP32Status(Base):
    __tablename__ = "esp32_status"  # Nombre de la tabla

    id = Column(Integer, primary_key=True, index=True)                           # ID único
    device_name = Column(String, unique=True, nullable=False)                   # Nombre del dispositivo ESP32
    mac_address = Column(String(17), nullable=False)                            # Dirección MAC del ESP32
    status = Column(String, nullable=False)                                     # Estado del dispositivo
    last_update = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())  # Fecha de última actualización

    __table_args__ = (
        # Restricción para que el estado solo sea "connected" o "disconnected"
        CheckConstraint(status.in_(["connected", "disconnected"]), name="valid_status"),
    )

# -------------------- Modelo: Usuarios --------------------
class User(Base):
    __tablename__ = "users"  # Nombre de la tabla

    id = Column(Integer, primary_key=True, index=True)                     # ID del usuario
    username = Column(String(50), unique=True, nullable=False)            # Nombre de usuario (único)
    email = Column(String(120), unique=True, nullable=False)              # Email (único)
    hashed_password = Column(String, nullable=False)                      # Contraseña hasheada
    is_admin = Column(Boolean, default=False)                             # Indica si es administrador
    created_at = Column(TIMESTAMP, server_default=func.now())             # Fecha de creación del usuario
