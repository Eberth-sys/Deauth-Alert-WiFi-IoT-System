#processing-layer\src\data_processor.py

# -------------------- Importaciones --------------------
import os                                                    # Para interactuar con el sistema operativo y acceder a variables de entorno
import asyncio                                               # Para manejar tareas asíncronas (aunque no se utiliza en este fragmento)
import requests                                              # Para realizar solicitudes HTTP
from datetime import datetime, timedelta                     # Para trabajar con fechas y tiempos (usado para timestamps y diferencias de tiempo)
from src.database import get_db_connection                   # Función para obtener la conexión con la base de datos
from src.mqtt_client import publish_alert                    # Función para publicar alertas en AWS IoT Core (MQTT)
from src.telegram_alert import enviar_mensaje_telegram       # Función para enviar alertas a Telegram
from dotenv import load_dotenv                               # Para cargar variables de entorno desde un archivo .env

# -------------------- Cargar configuración desde .env --------------------
load_dotenv()

# -------------------- Configuración de entorno --------------------
BACKEND_URL = os.getenv("BACKEND_URL")  # Cargar la URL base del backend desde el archivo .env
if not BACKEND_URL:
    raise ValueError("[CONFIG] ❌ Variable BACKEND_URL no definida en .env")  # Lanzar error si la variable no está definida


# -------------------- Variables de almacenamiento temporal --------------------
alerta_reciente = {}  # Diccionario para evitar el envío repetido de alertas en un corto período de tiempo
estado_nodos_previos = {}  # Diccionario para almacenar el estado previo de los nodos ESP32

# -------------------- Función: Guardar alerta de desautenticación --------------------
def guardar_alerta(nodo_iot, spoofed_bssid, bssid, target_mac, canal):
    conn = get_db_connection()  # Obtener conexión a la base de datos
    if conn is None:
        print("[ALERT] - No se pudo conectar a la base de datos.")
        return

    try:
        cursor = conn.cursor()
        # Guardar la alerta en la base de datos
        cursor.execute(""" 
            INSERT INTO alerts (nodo_iot, spoofed_bssid, bssid, target_mac, canal, timestamp) 
            VALUES (%s, %s, %s, %s, %s, NOW())
        """, (nodo_iot, spoofed_bssid, bssid, target_mac, int(canal)))
        conn.commit()  # Confirmar la transacción
        cursor.close() # Cerrar cursor
        conn.close()   # Cerrar conexión

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

        # -------------------- Filtro de alertas duplicadas --------------------
        clave_alerta = f"{nodo_iot}_{target_mac}_{canal}"  # Crea una clave única por alerta
        ahora = datetime.now()

        if clave_alerta in alerta_reciente:
            ultima_vez = alerta_reciente[clave_alerta]  # Fecha de la última alerta con la misma clave
            if (ahora - ultima_vez).total_seconds() < 30:  # Si la alerta se repite en menos de 10 segundos, se ignora
                print("[INFO] ⏳ Alerta ignorada por repetición reciente.")
                return
        alerta_reciente[clave_alerta] = ahora  # Actualiza la última vez que se recibió la alerta

        # -------------------- Enviar alerta a Telegram --------------------
        mensaje = (
            f"🚨 Alerta de Desautenticación Detectada\n"
            f"🔹 Nodo: {nodo_iot}\n"
            f"📡 Canal: {canal}\n"
            f"🎯 MAC objetivo: {target_mac}\n"
            f"🎭 BSSID suplantado: {spoofed_bssid}"
        )
        print("📤 Enviando mensaje a Telegram...")
        enviar_mensaje_telegram(mensaje)  # Enviar la alerta a Telegram

    except Exception as e:
        print(f"[ERROR] ❌ Error al guardar la alerta en la base de datos: {e}")

# -------------------- Función: Actualizar el estado de los nodos ESP32 --------------------
def actualizar_estado_esp32(device_name, mac_address, status):
    conn = get_db_connection()  # Obtener la conexión a la base de datos
    if conn is None:
        print("[ALERT] - No se pudo conectar a la base de datos.")
        return

    try:
        cursor = conn.cursor()
        # Actualiza o inserta el estado del dispositivo en la base de datos
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
        conn.commit()  # Confirmar transacción
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

        # -------------------- Enviar estado del nodo a Telegram --------------------
        if device_name not in estado_nodos_previos or estado_nodos_previos[device_name] != status:
            estado_nodos_previos[device_name] = status  # Actualizar estado previo del nodo

            estado = status.strip().lower()  # Procesar el estado
            estado_humano = "✅ Conectado" if estado in ["online", "connected"] else "❌ Desconectado"

            mensaje = (
                f"📡 *Estado del nodo actualizado*\n"
                f"🔹 Nodo: {device_name}\n"
                f"🔄 Estado: {estado_humano}\n"
                f"🕒 Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            print(f"📤 Enviando estado del nodo '{device_name}' a Telegram...")
            enviar_mensaje_telegram(mensaje)  # Enviar estado del nodo a Telegram

    except Exception as e:
        print(f"[ERROR] ❌ Error al actualizar el estado del ESP32 en la base de datos: {e}")

# -------------------- Función: Obtener estado de los nodos ESP32 --------------------
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

        # Devuelve un diccionario con la información de cada dispositivo
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
