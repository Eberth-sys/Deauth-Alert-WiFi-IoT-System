# src/utils.py

import yaml

# Cargar configuración desde devices.yaml
def load_config(path="config/devices.yaml"):
    try:
        with open(path, "r") as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        print(f"[ERROR] - No se encontró el archivo de configuración: {path}")
        return None  # Retorna None en vez de salir del programa
    except yaml.YAMLError as e:
        print(f"[ERROR] - Error al parsear el archivo YAML: {e}")
        return None  # Retorna None en vez de salir del programa

# Función para validar dispositivos permitidos
def is_device_allowed(address, devices):
    if not devices:
        print("[WARNING] - No hay dispositivos configurados en devices.yaml")
        return False
    return any(device["address"] == address for device in devices)
