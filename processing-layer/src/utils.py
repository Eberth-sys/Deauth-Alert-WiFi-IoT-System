# src/utils.py

import yaml

# Cargar configuración desde devices.yaml
def load_config(path="config/devices.yaml"):
    try:
        with open(path, "r") as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        print(f"[ERROR] Archivo de configuración no encontrado en: {path}")
        exit(1)
    except yaml.YAMLError as e:
        print(f"[ERROR] Error al parsear el archivo YAML: {e}")
        exit(1)
    
# Función para validar dispositivos permitidos
def is_device_allowed(address, devices):
    return any(device["address"] == address for device in devices)
