#processing-layer\src\data_processor.py
# -------------------- Importaciones --------------------
import os                                # Acceso al sistema operativo para interactuar con archivos y variables de entorno
import asyncio                           # Importación para manejar tareas asíncronas (aunque no se usa en este fragmento)
import requests                          # Para hacer peticiones HTTP (usado en el envío de actualizaciones al backend)
from datetime import datetime, timedelta # Para manejar fechas y tiempos (usado en la creación de timestamp y validación de alertas)
from src.database import get_db_connection # Función para obtener conexión a la base de datos
from src.mqtt_client import publish_alert  # Función para publicar alertas en AWS IoT Core (MQTT)
from src.telegram_alert import enviar_mensaje_telegram  # Función para enviar alertas a Telegram
from dotenv import load_dotenv           # Para cargar variables de entorno desde un archivo .env

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# -------------------- Configuración de entorno --------------------
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")  # URL del backend, valor por defecto es local

# -------------------- Memoria temporal para alertas recientes --------------------
alerta_reciente = {}  # Diccionario para almacenar las alertas recientes y evitar repeticiones

# -------------------- Función: Guardar evento de alerta --------------------
def guardar_alerta(nodo_iot, spoofed_bssid, bssid, target_mac, canal):
    conn = get_db_connection()  # Obtener la conexión a la base de datos
    if conn is None:
        print("[ALERT] - No se pudo conectar a la base de datos.")
        return

    try:
        cursor = conn.cursor()
        # Inserta la alerta en la base de datos
        cursor.execute(""" 
            INSERT INTO alerts (nodo_iot, spoofed_bssid, bssid, target_mac, canal, timestamp) 
            VALUES (%s, %s, %s, %s, %s, NOW())
        """, (nodo_iot, spoofed_bssid, bssid, target_mac, int(canal)))
        conn.commit()  # Confirma la transacción
        cursor.close() # Cierra el cursor
        conn.close()   # Cierra la conexión a la base de datos

        # -------------------- Publicar alerta en AWS IoT --------------------
        alert_data = {
            "nodo_iot": nodo_iot,
            "spoofed_bssid": spoofed_bssid,
            "bssid": bssid,
            "target_mac": target_mac,
            "canal": canal,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        publish_alert(alert_data)  # Publica la alerta en AWS IoT Core (MQTT)

        # -------------------- Filtro para evitar alertas duplicadas --------------------
        clave_alerta = f"{nodo_iot}_{target_mac}_{canal}"  # Crea una clave única para cada alerta
        ahora = datetime.now()

        if clave_alerta in alerta_reciente:
            ultima_vez = alerta_reciente[clave_alerta]  # Tiempo de la última alerta para el mismo nodo
            if (ahora - ultima_vez).total_seconds() < 30:  # Ignora alertas si se repiten en menos de 30 segundos
                print("[INFO] ⏳ Alerta ignorada por repetición reciente.")
                return  # No enviar alerta a Telegram

        alerta_reciente[clave_alerta] = ahora  # Actualiza la memoria con la última alerta

        # -------------------- Enviar alerta a Telegram --------------------
        mensaje = (
            f"🚨 Alerta de Desautenticación Detectada\n"
            f"🔹 Nodo: {nodo_iot}\n"
            f"📡 Canal: {canal}\n"
            f"🎯 MAC objetivo: {target_mac}\n"
            f"🎭 BSSID suplantado: {spoofed_bssid}"
        )
        print("📤 Enviando mensaje a Telegram...")
        enviar_mensaje_telegram(mensaje)  # Envía el mensaje a Telegram

    except Exception as e:
        print(f"[ERROR] ❌ Error al guardar la alerta en la base de datos: {e}")

# -------------------- Función: Actualizar estado del ESP32 --------------------
def actualizar_estado_esp32(device_name, mac_address, status):
    conn = get_db_connection()  # Obtener la conexión a la base de datos
    if conn is None:
        print("[ALERT] - No se pudo conectar a la base de datos.")
        return

    try:
        cursor = conn.cursor()
        # Actualiza el estado del dispositivo en la base de datos
        cursor.execute(""" 
            INSERT INTO esp32_status (device_name, mac_address, status, last_update) 
            VALUES (%s, %s, %s, NOW())
            ON CONFLICT (device_name) 
            DO UPDATE SET 
                status = EXCLUDED.status, 
                last_update = CASE 
                    WHEN esp32_status.status <> EXCLUDED.status THEN NOW() 
                    ELSE esp32_status.last_update 
                END;
        """, (device_name, mac_address, status))
        conn.commit()  # Confirma la transacción
        cursor.close()
        conn.close()

        # -------------------- Enviar actualización al backend --------------------
        status_data = {
            "device_name": device_name,
            "mac_address": mac_address,
            "status": status,
            "last_update": datetime.now().isoformat()
        }

        try:
            response = requests.post(f"{BACKEND_URL}/esp32-nodes/update", json=status_data, timeout=3)
            if response.status_code == 200:
                print(f"[INFO] 🔄 Estado de {device_name} actualizado y enviado al backend.")
            else:
                print(f"[WARNING] ⚠️ No se pudo enviar la actualización del ESP32 al backend: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] ❌ No se pudo conectar al backend: {e}")

    except Exception as e:
        print(f"[ERROR] ❌ Error al actualizar el estado del ESP32 en la base de datos: {e}")

# -------------------- Función: Obtener estado de los ESP32 --------------------
def obtener_estado_esp32():
    conn = get_db_connection()  # Obtener la conexión a la base de datos
    if conn is None:
        print("[ALERT] - No se pudo conectar a la base de datos.")
        return {}

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT device_name, mac_address, status, last_update FROM esp32_status;")
        dispositivos = cursor.fetchall()  # Recupera todos los dispositivos y su estado
        cursor.close()
        conn.close()

        # Devuelve un diccionario con los estados de los dispositivos
        return {
            device[0]: {  # Dispositivo (device_name) como clave
                "mac_address": device[1],
                "status": device[2],
                "last_update": device[3].strftime("%Y-%m-%d %H:%M:%S")
            }
            for device in dispositivos
        }

    except Exception as e:
        print(f"[ERROR] ❌ Error al obtener el estado de los ESP32 desde la base de datos: {e}")
        return {}
