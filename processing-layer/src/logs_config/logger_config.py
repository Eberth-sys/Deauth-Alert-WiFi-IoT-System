#/src/logs_config/logger_config.py

# -------------------- Importaciones --------------------
import logging                                 # Módulo estándar para manejo de logs
from logging.handlers import RotatingFileHandler  # Manejador para rotación automática de archivos de log
import os                                      # Para operaciones con el sistema de archivos

# -------------------- Directorio y archivo de logs --------------------
LOGS_DIR = "logs"                              # Carpeta donde se almacenarán los archivos de log
os.makedirs(LOGS_DIR, exist_ok=True)           # Crear carpeta si no existe

LOG_FILE = os.path.join(LOGS_DIR, "ble_events.log")  # Ruta completa del archivo de log

# -------------------- Configuración del manejador de log --------------------
log_handler = RotatingFileHandler(
    LOG_FILE,               # Ruta del archivo de log
    maxBytes=5 * 1024 * 1024,  # Tamaño máximo por archivo: 5 MB
    backupCount=3,          # Número máximo de archivos antiguos a conservar
    encoding="utf-8"        # Codificación para permitir caracteres especiales
)

# -------------------- Formato de los mensajes de log --------------------
log_formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s",  # Formato: fecha, nivel y mensaje
    datefmt="%Y-%m-%d %H:%M:%S"                   # Formato de fecha y hora
)
log_handler.setFormatter(log_formatter)

# -------------------- Inicialización del logger --------------------
logger = logging.getLogger("BLE_Logger")  # Nombre del logger
logger.setLevel(logging.INFO)             # Nivel mínimo de mensajes a registrar
logger.addHandler(log_handler)            # Asignación del manejador configurado
