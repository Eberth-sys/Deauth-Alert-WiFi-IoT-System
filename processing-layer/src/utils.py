# src/utils.py

# -------------------- Importaciones --------------------
import yaml  # Para cargar y parsear archivos YAML

# -------------------- Función: Cargar configuración desde archivo YAML --------------------
def load_config(path="config/devices.yaml"):
    """
    Carga la configuración de dispositivos y UUIDs desde un archivo YAML.
    :param path: Ruta del archivo YAML de configuración.
    :return: Diccionario con la configuración o None si ocurre un error.
    """
    try:
        with open(path, "r") as file:
            return yaml.safe_load(file)  # Carga segura del contenido YAML
    except FileNotFoundError:
        print(f"[ERROR] - No se encontró el archivo de configuración: {path}")
        return None
    except yaml.YAMLError as e:
        print(f"[ERROR] - Error al parsear el archivo YAML: {e}")
        return None

# -------------------- Función: Verificar si un dispositivo está permitido --------------------
def is_device_allowed(address, devices):
    """
    Verifica si una dirección MAC corresponde a un dispositivo permitido.
    :param address: Dirección MAC del dispositivo detectado.
    :param devices: Lista de dispositivos autorizados desde el archivo YAML.
    :return: True si el dispositivo está permitido, False en caso contrario.
    """
    if not devices:
        print("[WARNING] - No hay dispositivos configurados en devices.yaml")
        return False
    return any(device["address"] == address for device in devices)
