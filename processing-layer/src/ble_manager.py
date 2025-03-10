# src/ble_manager.py

from bleak import BleakClient, BleakScanner                              # Librería para gestionar conexiones BLE
import asyncio                                                           # Para manejar tareas asíncronas
from src.data_processor import guardar_alerta, actualizar_estado_esp32   # Ahora usamos la BD para guardar estados
from src.logs_config.logger_config import logger                         # Importamos el logger


class BLEManager:
    def __init__(self, devices, service_uuid, characteristic_uuid):
        self.devices = devices                                                 # Lista de ESP32 que queremos conectar
        self.service_uuid = service_uuid                                       # UUID del servicio BLE que transmite datos
        self.characteristic_uuid = characteristic_uuid                         # UUID de la característica que envía los datos
        self.device_status = {device["address"]: False for device in devices}  # Estado de conexión
		
    async def handle_device(self, device):  # Manejo de cada ESP32
        while True:  # Bucle infinito para intentar la conexión de los ESP32
            try:
                # - Reiniciar el escaneo de dispositivos antes de cada búsqueda
                await BleakScanner.discover(timeout=1)

                msg = f"[INFO] Buscando {device['name']} ({device['address']})..."
                print(msg)
                logger.info(msg.replace("[INFO] ", ""))

                found_device = await BleakScanner.find_device_by_address(device["address"], timeout=10)

                if not found_device:
                    # - Siempre registrar el mensaje CRITICAL cuando un ESP32 desaparece
                    msg = f"[DISCONNECTED] {device['name']} se ha desconectado."
                    print(msg)
                    logger.critical(msg.replace("[DISCONNECTED] ", ""))

                    #  Siempre actualizar el estado en la base de datos
                    actualizar_estado_esp32(device["name"], device["address"], "disconnected")

                    self.device_status[device["address"]] = False
                    actualizar_estado_esp32(device["name"], device["address"], "disconnected")  # Guardamos en PostgreSQL

                    msg = f"[WARNING] {device['name']} no encontrado. Reintentando en 10 segundos..."
                    print(msg)
                    logger.warning(msg.replace("[WARNING] ", ""))
                    await asyncio.sleep(10)
                    continue

                msg = f"[INFO] Intentando conectar a {device['name']}..."
                print(msg)
                logger.info(msg.replace("[INFO] ", ""))

                async with BleakClient(device["address"]) as client:
                    if client.is_connected:
                        self.device_status[device["address"]] = True  
                        msg = f"[CONNECTED] ✅ Conectado a {device['name']}"
                        print(msg)
                        logger.info(msg.replace("[CONNECTED] ✅ ", ""))
                        actualizar_estado_esp32(device["name"], device["address"], "connected")  # Guardamos en PostgreSQL

                        try:
                            await client.pair(protection_level=2)
                            msg = f"[SECURE] 🔒 Conexión cifrada con {device['name']}"
                            print(msg)
                            logger.info(msg.replace("[SECURE] 🔒 ", ""))
                        except Exception as e:
                            msg = f"[WARNING] No se pudo cifrar la conexión: {e}"
                            print(msg)
                            logger.warning(msg.replace("[WARNING] ", ""))

                        def notification_handler(sender, data):
                            decoded_data = data.decode('utf-8')

                            if "[ALERT]" in decoded_data:
                                msg = f"[DATA] {device['name']}: {decoded_data}"
                                print(msg)

                                try:
                                    partes = decoded_data.split(" | ")
                                    spoofed_bssid = partes[1].split(": ")[1].strip()
                                    target_mac = partes[2].split(": ")[1].strip()
                                    bssid = partes[3].split(": ")[1].strip()
                                    canal = int(partes[4].split(": ")[1].strip())
                                    nodo_iot = device['name']

                                    guardar_alerta(nodo_iot, spoofed_bssid, target_mac, bssid, canal)

                                except Exception as e:
                                    msg = f"[ERROR] Error al procesar los datos BLE: {e}"
                                    print(msg)
                                    logger.error(msg.replace("[ERROR] ", ""))

                        await client.start_notify(self.characteristic_uuid, notification_handler)
                        msg = f"[INFO] Esperando datos de {device['name']}..."
                        print(msg)
                        logger.info(msg.replace("[INFO] ", ""))

                        while client.is_connected:
                            await asyncio.sleep(1)

            except Exception as e:
                error_message = str(e)

                if "org.bluez.Error.InProgress" in error_message:
                    msg = "[ERROR] BlueZ ocupado. Esperando 10 segundos antes de reintentar..."
                    print(msg)
                    logger.error(msg.replace("[ERROR] ", ""))
                    await asyncio.sleep(10)  
                elif "Characteristic" in error_message:
                    msg = f"[ERROR] Error con {device['name']}: No se pudo acceder a la característica."
                    print(msg)
                    logger.error(msg.replace("[ERROR] ", ""))
                else:
                    msg = f"[ERROR] Error con {device['name']}: {error_message}"
                    print(msg)
                    logger.error(msg.replace("[ERROR] ", ""))

                msg = f"[DISCONNECTED] Reintentando conexión con {device['name']} en 10 segundos..."
                print(msg)
                logger.info(msg.replace("[DISCONNECTED] ", ""))
                actualizar_estado_esp32(device["name"], device["address"], "disconnected")   # Guardamos en PostgreSQL
                await asyncio.sleep(10)  

    async def run(self):
        """Ejecuta la conexión a los dispositivos en paralelo, evitando bloqueos."""
        tasks = [asyncio.create_task(self.handle_device(device)) for device in self.devices]
        await asyncio.gather(*tasks)
