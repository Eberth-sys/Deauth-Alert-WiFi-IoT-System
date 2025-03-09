# data_processor.py

from datetime import datetime
from src.database import get_db_connection  # Importamos la conexión centralizada

# Función para guardar eventos de ataque en la base de datos
def guardar_alerta(nodo_iot, spoofed_bssid, bssid, target_mac, canal):

    conn = get_db_connection()  # Obtener la conexión a la base de datos
    if conn is None:
        print("[ALERT] - No se pudo conectar a la base de datos.")
        return  # Si no hay conexión, no se hace nada.

    try:
        cursor = conn.cursor()  # Crea un cursor para ejecutar consultas SQL

        # Insertar el evento sin verificar duplicados
        cursor.execute("""
            INSERT INTO alerts (nodo_iot, spoofed_bssid, bssid, target_mac, canal, timestamp) 
            VALUES (%s, %s, %s, %s, %s, NOW())
        """, (nodo_iot, spoofed_bssid, bssid, target_mac, int(canal)))  # Convierte canal a int antes de insertar

        conn.commit()  # Guarda los cambios en la base de datos
        cursor.close()  # Cierra el cursor para liberar recursos
        conn.close()  # Cierra la conexión con la base de datos para evitar fugas de memoria

    except Exception as e:
        print(f"[ERROR] ❌ Error al guardar la alerta en la base de datos: {e}")

# Función para actualizar el estado de los ESP32 en la base de datos
def actualizar_estado_esp32(device_name, mac_address, status):
    """
    Actualiza el estado del ESP32 en la base de datos.
    Si no existe, lo crea.
    """
    conn = get_db_connection()
    if conn is None:
        print("[ALERT] - No se pudo conectar a la base de datos.")
        return

    try:
        cursor = conn.cursor()

        # Inserta o actualiza el estado del ESP32 en la base de datos
        cursor.execute("""
            INSERT INTO esp32_status (device_name, mac_address, status, last_update) 
            VALUES (%s, %s, %s, NOW())
            ON CONFLICT (device_name) 
            DO UPDATE SET status = EXCLUDED.status, last_update = NOW();
        """, (device_name, mac_address, status))

        conn.commit()
        cursor.close()
        conn.close()

    except Exception as e:
        print(f"[ERROR] ❌ Error al actualizar el estado del ESP32 en la base de datos: {e}")

# Función para obtener el estado actual de los ESP32 desde la base de datos
def obtener_estado_esp32():
    """
    Devolverá un diccionario con el estado actual de todos los ESP32 registrados en la base de datos.
    """
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
        estado_esp32 = {
            device[0]: {
                "mac_address": device[1],
                "status": device[2],
                "last_update": device[3].strftime("%Y-%m-%d %H:%M:%S")
            }
            for device in dispositivos
        }

        return estado_esp32

    except Exception as e:
        print(f"[ERROR] ❌ Error al obtener el estado de los ESP32 desde la base de datos: {e}")
        return {}