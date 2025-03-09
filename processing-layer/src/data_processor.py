import os
import asyncio
import requests  # Importamos requests para hacer peticiones HTTP al backend
from datetime import datetime
from src.database import get_db_connection  # Importamos la conexión centralizada

# Cargar la URL del backend desde las variables de entorno
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")  

# Función para guardar eventos de ataque en la base de datos
def guardar_alerta(nodo_iot, spoofed_bssid, bssid, target_mac, canal):
    conn = get_db_connection()
    if conn is None:
        print("[ALERT] - No se pudo conectar a la base de datos.")
        return

    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO alerts (nodo_iot, spoofed_bssid, bssid, target_mac, canal, timestamp) 
            VALUES (%s, %s, %s, %s, %s, NOW())
        """, (nodo_iot, spoofed_bssid, bssid, target_mac, int(canal)))  # Convierte canal a int

        conn.commit()
        cursor.close()
        conn.close()

    except Exception as e:
        print(f"[ERROR] ❌ Error al guardar la alerta en la base de datos: {e}")

# Función para actualizar el estado de los ESP32 en la base de datos y notificar al backend
def actualizar_estado_esp32(device_name, mac_address, status):
    conn = get_db_connection()
    if conn is None:
        print("[ALERT] - No se pudo conectar a la base de datos.")
        return

    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO esp32_status (device_name, mac_address, status, last_update) 
            VALUES (%s, %s, %s, NOW())
            ON CONFLICT (device_name) 
            DO UPDATE SET status = EXCLUDED.status, last_update = NOW();
        """, (device_name, mac_address, status))

        conn.commit()
        cursor.close()
        conn.close()

        # Enviar actualización al backend vía HTTP
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

# Función para obtener el estado actual de los ESP32 desde la base de datos
def obtener_estado_esp32():
    conn = get_db_connection()
    if conn is None:
        print("[ALERT] - No se pudo conectar a la base de datos.")
        return {}

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT device_name, mac_address, status, last_update FROM esp32_status;")
        dispositivos = cursor.fetchall()
        cursor.close()
        conn.close()

        # Convertimos los resultados en un diccionario
        return {
            device[0]: {
                "mac_address": device[1],
                "status": device[2],
                "last_update": device[3].strftime("%Y-%m-%d %H:%M:%S")
            }
            for device in dispositivos
        }

    except Exception as e:
        print(f"[ERROR] ❌ Error al obtener el estado de los ESP32 desde la base de datos: {e}")
        return {}
