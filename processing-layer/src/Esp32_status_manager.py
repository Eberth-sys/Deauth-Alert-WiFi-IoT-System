# /src/Esp32_status_manager.py

# -------------------- Descripción --------------------
"""Estado actual de los dispositivos nodos IoT ESP32 en formato JSON."""

# -------------------- Importaciones --------------------
import json                               # Para trabajar con archivos JSON
import os                                 # Para gestionar rutas y archivos
from datetime import datetime             # Para registrar la fecha y hora de actualización

# -------------------- Ruta del archivo de estado --------------------
STATUS_FILE = "logs/Esp32_status.json"  # Ruta donde se guarda el estado de los ESP32

# -------------------- Inicialización del archivo de estado --------------------
def initialize_status_file():
    """
    Crea la carpeta y el archivo de estado si no existen.
    """
    os.makedirs(os.path.dirname(STATUS_FILE), exist_ok=True)  # Asegura que exista la carpeta 'logs/'
    if not os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, "w") as f:
            json.dump({}, f, indent=4)  # Inicializa el archivo como un diccionario vacío

# -------------------- Función: Actualizar estado de un ESP32 --------------------
def update_device_status(device_name, status):
    """
    Actualiza el estado de un dispositivo ESP32 en el archivo JSON.
    :param device_name: Nombre identificador del dispositivo.
    :param status: Estado actual del dispositivo (e.g., 'connected', 'disconnected').
    """
    try:
        with open(STATUS_FILE, "r") as f:
            status_data = json.load(f)  # Cargar datos actuales
    except (json.JSONDecodeError, FileNotFoundError):
        status_data = {}

    # Actualizar información del dispositivo
    status_data[device_name] = {
        "status": status,
        "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    # Guardar los datos actualizados
    with open(STATUS_FILE, "w") as f:
        json.dump(status_data, f, indent=4)

# -------------------- Función: Obtener estado actual de los dispositivos --------------------
def get_device_status():
    """
    Devuelve el estado actual de todos los dispositivos desde el archivo JSON.
    :return: Diccionario con la información de estado.
    """
    try:
        with open(STATUS_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}

# -------------------- Inicializar archivo al cargar el módulo --------------------
initialize_status_file()