#src/ble_manager.py

from bleak import BleakClient, BleakScanner
import asyncio
from datetime import datetime
from src.data_processor import process_data

class BLEManager:
    def __init__(self, devices, service_uuid, characteristic_uuid):
        self.devices = devices
        self.service_uuid = service_uuid
        self.characteristic_uuid = characteristic_uuid

    async def handle_device(self, device):
        while True:
            try:
                print(f"[INFO] Buscando {device['name']} ({device['address']})...")
                found_device = await BleakScanner.find_device_by_address(device["address"], timeout=10)

                if not found_device:
                    print(f"[WARNING] {device['name']} no encontrado. Reintentando en 10 segundos...")
                    await asyncio.sleep(10)
                    continue

                print(f"[INFO] Intentando conectar a {device['name']}...")
                async with BleakClient(device["address"]) as client:
                    if client.is_connected:
                        print(f"[CONNECTED] Conectado a {device['name']}")

                        await client.pair(protection_level=2)
                        print(f"[SECURE] Conexión cifrada con {device['name']}")

                        def notification_handler(sender, data):
                            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            decoded_data = data.decode('utf-8')
                            print(f"[DATA] [{timestamp}] {device['name']}: {decoded_data}")
                            process_data(device['name'], decoded_data, timestamp)

                        await client.start_notify(self.characteristic_uuid, notification_handler)
                        print(f"[INFO] Esperando datos de {device['name']}...")

                        while client.is_connected:
                            await asyncio.sleep(1)

            except Exception as e:
                if "Characteristic" in str(e):
                    print(f"[ERROR] Error con {device['name']}: No se pudo acceder a la característica.")
                else:
                    print(f"[ERROR] Error con {device['name']}: {str(e)}")
                print(f"[DISCONNECTED] Reintentando conexión con {device['name']} en 10 segundos...")
                await asyncio.sleep(10)

    async def run(self):
        tasks = [self.handle_device(device) for device in self.devices]
        await asyncio.gather(*tasks)
