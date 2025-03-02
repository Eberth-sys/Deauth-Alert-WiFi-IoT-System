#utils.py
import asyncio
from src.ble_manager import BLEManager
from src.utils import load_config
from src.database import get_db_connection  # Importamos la conexión centralizada

async def main():
    # Cargar configuración desde devices.yaml
    config = load_config("config/devices.yaml")

    if not config:
        print("[ALERT] - No se pudo cargar la configuración. Verifica 'devices.yaml'.")
        return  # Evita continuar si no hay configuración

    # Verificar si hay dispositivos en la configuración
    devices = config.get('esp32_devices', [])
    uuids = config.get('uuids', {})

    if not devices or not uuids:
        print("[ALERT] - No hay dispositivos o UUIDs en la configuración.")
        return

    # Probar conexión a PostgreSQL
    conn = get_db_connection()
    if conn:
        print("[INFO] - Conexión exitosa a PostgreSQL en Docker!")
        conn.close()
    else:
        print("[ALERT] - No se pudo conectar a la base de datos.")
        return  # Evita continuar si no hay conexión a la BD

    # Inicializar BLEManager
    ble_manager = BLEManager(devices, uuids.get('service_uuid'), uuids.get('characteristic_uuid'))
    
    try:
        await ble_manager.run()
    except Exception as e:
        print(f"[ERROR] - Error en BLEManager: {e}")

if __name__ == "__main__":
    asyncio.run(main())
