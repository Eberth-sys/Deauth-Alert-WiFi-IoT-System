#/src/logs_config/logger_config.py

import logging
from logging.handlers import RotatingFileHandler
import os

# Condición para asegurar que la carpeta de logs exista
LOGS_DIR = "logs"
os.makedirs(LOGS_DIR, exist_ok=True)

# Configuración sistema de logging con rotación automática
LOG_FILE = os.path.join(LOGS_DIR, "ble_events.log")

log_handler = RotatingFileHandler(
    LOG_FILE,                         # Archivo de logs
    maxBytes=5 * 1024 * 1024,         # Máximo 5MB por archivo
    backupCount=3,                    # Mantener hasta 3 archivos de logs anteriores
    encoding="utf-8"                  # Asegura compatibilidad con caracteres especiales
)

# Defino el formato del log
log_formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
log_handler.setFormatter(log_formatter)

#Configuración del logger
logger = logging.getLogger("BLE_Logger")
logger.setLevel(logging.INFO)
logger.addHandler(log_handler)

