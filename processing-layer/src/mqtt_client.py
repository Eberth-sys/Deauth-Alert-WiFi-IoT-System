#processing-layer\src\mqtt_client.py

# -------------------- Importaciones --------------------
import paho.mqtt.client as mqtt            # Cliente MQTT de Paho
import ssl                                 # Para configurar conexión segura TLS
import os                                  # Para acceder a variables de entorno
import json                                # Para convertir alertas a formato JSON
import time                                # Para gestionar intervalos de reconexión
from dotenv import load_dotenv             # Para cargar configuración desde archivo .env

# -------------------- Cargar archivo .env --------------------
load_dotenv()  # Carga las variables de entorno definidas en el archivo .env

# -------------------- Parámetros de conexión MQTT --------------------
ENDPOINT = os.getenv("MQTT_ENDPOINT")                 # Dirección del broker MQTT (AWS IoT Core)
CLIENT_ID = os.getenv("MQTT_CLIENT_ID", "RaspberryPi-IoT")  # ID del cliente MQTT
TOPIC = os.getenv("MQTT_TOPIC", "alerts/deauthentication")  # Tema de publicación
ROOT_CA = os.getenv("MQTT_ROOT_CA")                   # Ruta del certificado raíz
CERT_FILE = os.getenv("MQTT_CERT_FILE")               # Ruta del certificado del cliente
KEY_FILE = os.getenv("MQTT_KEY_FILE")                 # Ruta de la clave privada del cliente

# Validación de archivos de configuración
if not all([ENDPOINT, ROOT_CA, CERT_FILE, KEY_FILE]):
    print("[ERROR] ❌ Faltan variables de configuración en el archivo .env.")
    exit(1)

# -------------------- Inicializar cliente MQTT --------------------
mqtt_client = mqtt.Client(CLIENT_ID)  # Crear cliente MQTT
mqtt_client.tls_set(
    ca_certs=ROOT_CA, 
    certfile=CERT_FILE, 
    keyfile=KEY_FILE, 
    tls_version=ssl.PROTOCOL_TLSv1_2  # Usar protocolo TLS versión 1.2
)

RECONNECT_DELAY = 5  # Tiempo (en segundos) para intentar reconexión

# -------------------- Callbacks del cliente --------------------
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Conexión exitosa a AWS IoT Core.")
    else:
        print(f"[ERROR] ❌ Fallo al conectarse. Código de error: {rc}")

def on_disconnect(client, userdata, rc):
    print(f"[WARNING] ⚠️ Conexión perdida. Intentando reconectar en {RECONNECT_DELAY} segundos...")
    time.sleep(RECONNECT_DELAY)
    try:
        client.reconnect()
    except Exception as e:
        print(f"[ERROR] ❌ No se pudo reconectar: {e}")

# Asignar funciones callback al cliente
mqtt_client.on_connect = on_connect
mqtt_client.on_disconnect = on_disconnect

# -------------------- Intentar conexión --------------------
connected = False
while not connected:
    try:
        mqtt_client.connect(ENDPOINT, 8883, 60)  # Conexión segura por el puerto 8883
        mqtt_client.loop_start()                # Inicia el loop en segundo plano
        connected = True
    except Exception as e:
        print(f"[ERROR] ❌ Error al conectar a AWS IoT Core: {e}")
        print(f"Reintentando en {RECONNECT_DELAY} segundos...")
        time.sleep(RECONNECT_DELAY)

# -------------------- Función: Publicar alerta MQTT --------------------
def publish_alert(alert_data):
    """
    Publica una alerta en formato JSON a AWS IoT Core.
    :param alert_data: Diccionario con la información de la alerta.
    """
    try:
        message_json = json.dumps(alert_data)  # Convertir el diccionario a JSON
        result = mqtt_client.publish(TOPIC, message_json)  # Publicar mensaje en el tópico MQTT
        
        if result.rc == 0:
            print(f"✅ Alerta enviada correctamente: {message_json}")
        else:
            print(f"[ERROR] ❌ Fallo al publicar la alerta. Código de error: {result.rc}")
    except Exception as e:
        print(f"[ERROR] ❌ Error al publicar alerta: {e}")
