#processing-layer\main.py

# -------------------- Importaciones --------------------
import asyncio                                        # Para ejecutar funciones asíncronas
from src.ble_manager import BLEManager               # Clase encargada de gestionar conexiones BLE
from src.utils import load_config                    # Función para cargar configuración desde archivo YAML
from src.database import get_db_connection           # Función centralizada para conectar con PostgreSQL

# -------------------- Función Principal --------------------
async def main():
    """
    Punto de entrada principal del sistema.
    - Carga la configuración de dispositivos.
    - Verifica la conexión a la base de datos.
    - Inicializa y ejecuta el gestor de dispositivos BLE.
    """

    # Cargar configuración desde archivo YAML
    config = load_config("config/devices.yaml")

    if not config:
        print("[ALERT] - No se pudo cargar la configuración. Verifica 'devices.yaml'.")
        return

    # Extraer listas de dispositivos y UUIDs desde el archivo
    devices = config.get('esp32_devices', [])
    uuids = config.get('uuids', {})

    if not devices or not uuids:
        print("[ALERT] - No hay dispositivos o UUIDs en la configuración.")
        return

    # Verificar conexión a la base de datos PostgreSQL
    conn = get_db_connection()
    if conn:
        print("[INFO] ✅ Conexión exitosa a PostgreSQL en Docker!")
        conn.close()
    else:
        print("[ALERT] ❌ No se pudo conectar a la base de datos.")
        return

    # Crear instancia del gestor BLE con los dispositivos y UUIDs configurados
    ble_manager = BLEManager(devices, uuids.get('service_uuid'), uuids.get('characteristic_uuid'))

    # Ejecutar el gestor BLE
    try:
        await ble_manager.run()
    except Exception as e:
        print(f"[ERROR] ❌ Error en BLEManager: {e}")

# -------------------- Ejecución del Script --------------------
if __name__ == "__main__":
    asyncio.run(main())  # Inicia la función principal usando asyncio
