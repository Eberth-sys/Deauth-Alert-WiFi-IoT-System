#src/ble_manager.py

from bleak import BleakClient, BleakScanner  # Librería para gestionar conexiones BLE
import asyncio  # Para manejar tareas asíncronas
from datetime import datetime
from src.data_processor import guardar_alerta  # Importa la función para guardar alertas en la base de datos

class BLEManager:
    def __init__(self, devices, service_uuid, characteristic_uuid):
        self.devices = devices  # Lista de ESP32 que queremos conectar
        self.service_uuid = service_uuid  # UUID del servicio BLE que transmite datos
        self.characteristic_uuid = characteristic_uuid  # UUID de la característica que envía los datos
        self.device_status = {device["address"]: False for device in devices}  # Estado de conexión

    async def handle_device(self, device):  # Manejo de cada ESP32
        while True:  # Bucle infinito para intentar la conexión de los ESP32
            try:
                print(f"[INFO] Buscando {device['name']} ({device['address']})...")
                # Escanear y buscar el ESP32 por 10 segundos
                found_device = await BleakScanner.find_device_by_address(device["address"], timeout=10)

                if not found_device:
                    if self.device_status[device["address"]]:  # Solo mostrar si estaba conectado antes
                        print(f"[DISCONNECTED] ❌ {device['name']} se ha desconectado.")
                        self.device_status[device["address"]] = False  # Marcar como desconectado

                    print(f"[WARNING] {device['name']} no encontrado. Reintentando en 10 segundos...")
                    await asyncio.sleep(10)  # Esperar 10 segundos antes de reintentar
                    continue  # Continuar buscando el dispositivo

                print(f"[INFO] Intentando conectar a {device['name']}...")
                async with BleakClient(device["address"]) as client:
                    if client.is_connected:
                        self.device_status[device["address"]] = True  # Marcar como conectado
                        print(f"[CONNECTED] ✅ Conectado a {device['name']}")

                        try:
                            await client.pair(protection_level=2)  # Intentar cifrar la conexión
                            print(f"[SECURE] 🔒 Conexión cifrada con {device['name']}")
                        except Exception as e:
                            print(f"[WARNING] No se pudo cifrar la conexión: {e}")

                        def notification_handler(sender, data):
                            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Fecha y hora del evento registrado
                            decoded_data = data.decode('utf-8')  # Convertir datos BLE en texto legible
                            print(f"[DATA] [{timestamp}] {device['name']}: {decoded_data}")

                            # Extraer los valores correctos del mensaje recibido
                            try:
                                if "[ALERT]" in decoded_data and "Origen:" in decoded_data:
                                    # Separar la cadena usando ' | ' como delimitador
                                    partes = decoded_data.split(" | ")

                                    # Extraer los valores clave del mensaje recibido
                                    spoofed_bssid = partes[1].split(": ")[1].strip()
                                    target_mac = partes[2].split(": ")[1].strip()  # Modificado por target_mac
                                    bssid = partes[3].split(": ")[1].strip()
                                    canal = int(partes[4].split(": ")[1].strip())
                                    nodo_iot = device['name']

                                    # Guardar en la base de datos
                                    guardar_alerta(nodo_iot, spoofed_bssid, target_mac, bssid, canal)  # Modificado por target_mac
                                    # print(f" Alerta guardada en la base de datos desde {device['name']}")

                                else:
                                    print(f"[WARNING] Formato de datos inesperado: {decoded_data}")

                            except Exception as e:
                                print(f"[ERROR] Error al procesar los datos BLE: {e}")

                        await client.start_notify(self.characteristic_uuid, notification_handler)
                        print(f"[INFO] Esperando datos de {device['name']}...")

                        while client.is_connected:
                            await asyncio.sleep(1)

            except Exception as e:  #Manejo de errores para intentos de coenxión.
                error_message = str(e)

                if "org.bluez.Error.InProgress" in error_message:
                    print(f"[ERROR] BlueZ ocupado. Esperando 10 segundos antes de reintentar...")
                    await asyncio.sleep(10)
                elif "Characteristic" in error_message:
                    print(f"[ERROR] Error con {device['name']}: No se pudo acceder a la característica.")
                else:
                    print(f"[ERROR] Error con {device['name']}: {error_message}")

                print(f"[DISCONNECTED] Reintentando conexión con {device['name']} en 10 segundos...")
                await asyncio.sleep(10)  # Espera 10 segundos antes de intentar reconectar

    async def run(self): #Conexión a los ESP32 en paralelo, evitando bloqueos.

        tasks = [asyncio.create_task(self.handle_device(device)) for device in self.devices]
        await asyncio.gather(*tasks)  # Procesar dispositivos en paralelo
