#main.py

import asyncio
from src.ble_manager import BLEManager
from src.utils import load_config

async def main():
    # Cargar configuración desde devices.yaml
    config = load_config("config/devices.yaml")
    devices = config['esp32_devices']
    uuids = config['uuids']

    # Inicializar BLEManager
    ble_manager = BLEManager(devices, uuids['service_uuid'], uuids['characteristic_uuid'])
    await ble_manager.run()

if __name__ == "__main__":
    asyncio.run(main())

