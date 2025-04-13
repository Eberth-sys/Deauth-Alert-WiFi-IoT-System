#processing-layer\src\mqtt_client.py

import paho.mqtt.client as mqtt
import ssl
import os
import json
import time
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Parámetros de conexión MQTT (cargados desde .env)
ENDPOINT = os.getenv("MQTT_ENDPOINT")
CLIENT_ID = os.getenv("MQTT_CLIENT_ID", "RaspberryPi-IoT")
TOPIC = os.getenv("MQTT_TOPIC", "alerts/deauthentication")
ROOT_CA = os.getenv("MQTT_ROOT_CA")
CERT_FILE = os.getenv("MQTT_CERT_FILE")
KEY_FILE = os.getenv("MQTT_KEY_FILE")

# Validar que todos los archivos necesarios existen
if not all([ENDPOINT, ROOT_CA, CERT_FILE, KEY_FILE]):
    print("[ERROR] ❌ Faltan variables de configuración en el archivo .env.")
    exit(1)

# Crear cliente MQTT
mqtt_client = mqtt.Client(CLIENT_ID)
mqtt_client.tls_set(ca_certs=ROOT_CA, certfile=CERT_FILE, keyfile=KEY_FILE, tls_version=ssl.PROTOCOL_TLSv1_2)

# Variables para reconexión
RECONNECT_DELAY = 5  # Tiempo en segundos antes de intentar reconectar

# Función que se ejecuta cuando se conecta exitosamente
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Conexión exitosa a AWS IoT Core.")
    else:
        print(f"[ERROR] ❌ Fallo al conectarse. Código de error: {rc}")

# Función que se ejecuta cuando se pierde la conexión
def on_disconnect(client, userdata, rc):
    print(f"[WARNING] ⚠️ Conexión perdida. Intentando reconectar en {RECONNECT_DELAY} segundos...")
    time.sleep(RECONNECT_DELAY)
    try:
        client.reconnect()
    except Exception as e:
        print(f"[ERROR] ❌ No se pudo reconectar: {e}")

# Asignar funciones al cliente MQTT
mqtt_client.on_connect = on_connect
mqtt_client.on_disconnect = on_disconnect

# Intentar conexión inicial
connected = False
while not connected:
    try:
        mqtt_client.connect(ENDPOINT, 8883, 60)
        mqtt_client.loop_start()
        connected = True
    except Exception as e:
        print(f"[ERROR] ❌ Error al conectar a AWS IoT Core: {e}")
        print(f"Reintentando en {RECONNECT_DELAY} segundos...")
        time.sleep(RECONNECT_DELAY)

def publish_alert(alert_data):
    """
    Publica una alerta en formato JSON a AWS IoT Core.
    :param alert_data: Diccionario con la información de la alerta.
    """
    try:
        message_json = json.dumps(alert_data)
        result = mqtt_client.publish(TOPIC, message_json)
        
        if result.rc == 0:
            print(f"✅ Alerta enviada correctamente: {message_json}")
        else:
            print(f"[ERROR] ❌ Fallo al publicar la alerta. Código de error: {result.rc}")
    except Exception as e:
        print(f"[ERROR] ❌ Error al publicar alerta: {e}")
