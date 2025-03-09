# backend/src/models.py

from sqlalchemy import Column, Integer, String, TIMESTAMP    # Define tipos de datos para las columnas de la tabla
from sqlalchemy.sql import func                              # Funciones SQL
from src.database import Base                                # Importa nuestra base de datos


# Definimos el modelo de la tabla "alerts" en la base de datos
class Alert(Base):
    __tablename__ = "alerts"                                       # Nombre de la tabla en PostgreSQL

    id = Column(Integer, primary_key=True, index=True, nullable=False)              # Identificador único
    nodo_iot = Column(String, nullable=False)                                       # Dispositivo que detectó el ataque
    spoofed_bssid = Column(String(17), nullable=False)                              # BSSID suplantado
    target_mac = Column(String(17), nullable=False)                                 # MAC de destino del ataque
    bssid = Column(String(17), nullable=False)                                      # BSSID original
    canal = Column(Integer, nullable=False)                                         # Canal donde se detectó el ataque
    timestamp = Column(TIMESTAMP, server_default=func.now())                        # Fecha y hora del evento
