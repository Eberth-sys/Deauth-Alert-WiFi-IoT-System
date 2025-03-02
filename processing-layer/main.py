#main.py

import asyncio
from src.ble_manager import BLEManager
from src.utils import load_config
from src.database import get_db_connection  # Importamos la conexión centralizada

async def main():
    # Cargar configuración desde devices.yaml
    config = load_config("config/devices.yaml")
    devices = config['esp32_devices']
    uuids = config['uuids']

    # Probar conexión a PostgreSQL
    conn = get_db_connection()
    if conn:
        print("[INFO] - Conexión exitosa a PostgreSQL en Docker!")
        conn.close()
    else:
        print("[ALERT] - No se pudo conectar a la base de datos.")

    # Inicializar BLEManager
    ble_manager = BLEManager(devices, uuids['service_uuid'], uuids['characteristic_uuid'])
    await ble_manager.run()

if __name__ == "__main__":
    asyncio.run(main())
