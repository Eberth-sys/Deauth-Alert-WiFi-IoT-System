#src/ble_manager.py

from bleak import BleakClient, BleakScanner  # Librería para gestionar conexiones BLE
import asyncio # Para manejar tareas asíncronas
from datetime import datetime
from src.data_processor import guardar_alerta  # Importa la función para guardar alertas en la base de datos

class BLEManager:
    def __init__(self, devices, service_uuid, characteristic_uuid):
        self.devices = devices  # Lista de ESP32 que queremos conectar
        self.service_uuid = service_uuid # UUID del servicio BLE que transmite datos
        self.characteristic_uuid = characteristic_uuid # UUID de la característica que envía los datos

    async def handle_device(self, device): #Manejo de cada ESP32
        while True: #Bucle infinito para intentar la conexión de los esp32
            try:
                print(f"[INFO] Buscando {device['name']} ({device['address']})...")
                #Escanear y buscar los esp32 por 10 segundos 
                found_device = await BleakScanner.find_device_by_address(device["address"], timeout=10)

                if not found_device:
                    print(f"[WARNING] {device['name']} no encontrado. Reintentando en 10 segundos...")
                    await asyncio.sleep(10) #esperar 10 segs
                    continue #continuo buscando el dispotivo.

                print(f"[INFO] Intentando conectar a {device['name']}...")
                async with BleakClient(device["address"]) as client:
                    if client.is_connected:
                        print(f"[CONNECTED] Conectado a {device['name']}")

                        await client.pair(protection_level=2)
                        print(f"[SECURE] Conexión cifrada con {device['name']}")

                        def notification_handler(sender, data):
                            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Fecha y hora del evento resgitrado
                            decoded_data = data.decode('utf-8')  # Convertir datos BLE en texto legible
                            print(f"[DATA] [{timestamp}] {device['name']}: {decoded_data}")

                            # Extraer los valores correctos del mensaje recibido
                            try:
                                if "[ALERT]" in decoded_data and "Origen:" in decoded_data:
                                    # Separar la cadena usando ' | ' como delimitador
                                    partes = decoded_data.split(" | ")

                                    # Extraer los valores clave del mensaje recibido
                                    spoofed_bssid = partes[1].split(": ")[1].strip()
                                    target_mac = partes[2].split(": ")[1].strip()  # Modifique el nombre por target_mac
                                    bssid = partes[3].split(": ")[1].strip()
                                    canal = int(partes[4].split(": ")[1].strip())
                                    nodo_iot = device['name']

                                    # Guardar en la base de datos
                                    guardar_alerta(nodo_iot, spoofed_bssid, target_mac, bssid, canal ) # Modifique el nombre por target_mac
                                   # print(f" Alerta guardada en la base de datos desde {device['name']}")

                                else:
                                    print(f"[WARNING] Formato de datos inesperado: {decoded_data}")

                            except Exception as e:
                                print(f"[ERROR] Error al procesar los datos BLE: {e}")

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
