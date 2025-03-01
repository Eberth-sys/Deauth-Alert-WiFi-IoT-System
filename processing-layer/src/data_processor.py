# src/data_processor.py

import psycopg2
import os

# Función para conectar con PostgreSQL
def conectar_db():
    try:
        return psycopg2.connect(
            dbname=os.getenv("PG_DB"),  # Nombre de la base de datos
            user=os.getenv("PG_USER"),  # Usuario de la base de datos
            password=os.getenv("PG_PASSWORD"), # Contraseña de la base de datos
            host=os.getenv("PG_HOST"), # Dirección del servidor (localhost)
            port=os.getenv("PG_PORT") # Puerto de PostgreSQL (5432)
        )
    except Exception as e:
        print(f"- > Error al conectar con la base de datos: {e}")
        return None

# Función para guardar eventos de ataque en la base de datos
def guardar_alerta(origen_mac, destino_mac, bssid, canal):
    conn = conectar_db()  #establecer una conexión con la base de datos
    if conn is None:
        return  # Si no hay conexión, no se hace nada.

    try:
        cursor = conn.cursor() # Crea un cursor para ejecutar consultas SQL
        cursor.execute("""
            INSERT INTO alerts (origen_mac, destino_mac, bssid, canal)
            VALUES (%s, %s, %s, %s)
        """, (origen_mac, destino_mac, bssid, canal)) #(%s) para evitar SQL Injection
        conn.commit()  # Guarda los cambios en la base de datos
        cursor.close() # Cierra el cursor para liberar recursos
        conn.close() # Cierra la conexión con la base de datos para evitar fugas de memoria
    except Exception as e:
        print(f" -> Error al guardar la alerta en la base de datos: {e}")
