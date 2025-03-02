from datetime import datetime, timedelta
from src.database import get_db_connection  # Importamos la conexión centralizada

# Función para guardar eventos de ataque en la base de datos
def guardar_alerta(nodo_iot, spoofed_bssid, bssid, destino_mac, canal):

    conn = get_db_connection()  # Obtener la conexión a la base de datos
    if conn is None:
        print("[ALERT] - No se pudo conectar a la base de datos.")
        return  # Si no hay conexión, no se hace nada.

    try:
        cursor = conn.cursor()  # Crea un cursor para ejecutar consultas SQL

        # Verificamos si ya existe un ataque similar en los últimos 5 segundos
        tiempo_limite = datetime.now() - timedelta(seconds=5)

        cursor.execute("""
            SELECT COUNT(*) FROM alerts
            WHERE nodo_iot = %s AND spoofed_bssid = %s AND bssid = %s 
            AND destino_mac = %s AND canal = %s AND timestamp >= %s;
        """, (nodo_iot, spoofed_bssid, bssid, destino_mac, canal, tiempo_limite))

        cantidad = cursor.fetchone()[0]

        if cantidad == 0:
            # Si no hay registros recientes, insertamos el nuevo ataque
            cursor.execute("""
                INSERT INTO alerts (nodo_iot, spoofed_bssid, bssid, destino_mac, canal)
                VALUES (%s, %s, %s, %s, %s)
            """, (nodo_iot, spoofed_bssid, bssid, destino_mac, canal))  # (%s) para evitar SQL Injection

            conn.commit()  # Guarda los cambios en la base de datos

            print(f"[INFO] - Alerta guardada en la base de datos desde {nodo_iot}")

        cursor.close()  # Cierra el cursor para liberar recursos
        conn.close()  # Cierra la conexión con la base de datos para evitar fugas de memoria

    except Exception as e:
        print(f"[ERROR] - Error al guardar la alerta en la base de datos: {e}")

