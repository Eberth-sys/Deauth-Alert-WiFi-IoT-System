# /src/Esp32_status_manager.py

"""Estado actual de los dispotivos nodos IoT Esp32 en formato JSON."""

import json
import os
from datetime import datetime

# Ubicación del archivo JSON donde se guardará el estado de los ESP32
STATUS_FILE = "logs/Esp32_status.json"


# Crear el archivo status.json si no existe
def initialize_status_file():
    os.makedirs(os.path.dirname(STATUS_FILE), exist_ok=True) #Asegura que la carpeta 'logs/' existe

    if not os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, "w") as f:
            json.dump({}, f, indent=4)

# Función para actualizar el estado de un ESP32
def update_device_status(device_name, status):
    """Actualizar el estado de los ESP32 en el archivo status.json."""
    try:
        with open(STATUS_FILE, "r") as f:
            status_data = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        status_data = {}

    # Actualizar el estado del dispositivo
    status_data[device_name] = {
        "status": status,
        "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    # Guardar los cambios en status.json
    with open(STATUS_FILE, "w") as f:
        json.dump(status_data, f, indent=4)

# Función para obtener el estado actual de los dispositivos
def get_device_status():
    """Obtener el estado actual de los dispositivos desde status.json."""
    try:
        with open(STATUS_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}

# Inicializar el archivo status.json si no existe
initialize_status_file()

