#src/ble_manager.py

from bleak import BleakClient, BleakScanner  # Librería para gestionar conexiones BLE
import asyncio  # Para manejar tareas asíncronas
import logging  # Librería para gestionar logs en un archivo
from src.data_processor import guardar_alerta  # Importa la función para guardar alertas en la base de datos

# Configuración del sistema de logging
logging.basicConfig(
    filename="logs/ble_events.log",  # Archivo donde se almacenarán los logs
    level=logging.INFO,  # Nivel de log (INFO para capturar eventos generales)
    format="%(asctime)s - %(levelname)s - %(message)s",  # Formato estándar de logs
    datefmt="%Y-%m-%d %H:%M:%S",  # Formato de fecha y hora en los logs
)

class BLEManager:
    def __init__(self, devices, service_uuid, characteristic_uuid):
        self.devices = devices  # Lista de ESP32 que queremos conectar
        self.service_uuid = service_uuid  # UUID del servicio BLE que transmite datos
        self.characteristic_uuid = characteristic_uuid  # UUID de la característica que envía los datos
        self.device_status = {device["address"]: False for device in devices}  # Estado de conexión

    async def handle_device(self, device):  # Manejo de cada ESP32
        while True:  # Bucle infinito para intentar la conexión de los ESP32
            try:
                msg = f"[INFO] Buscando {device['name']} ({device['address']})..."
                print(msg)  # Mantiene el formato con corchetes en consola
                logging.info(msg.replace("[INFO] ", ""))  # Guarda en logs sin corchetes

                # Escanear y buscar el ESP32 por 10 segundos
                found_device = await BleakScanner.find_device_by_address(device["address"], timeout=10)

                if not found_device:
                    if self.device_status[device["address"]]:  # Solo mostrar si estaba conectado antes
                        msg = f"[DISCONNECTED] {device['name']} se ha desconectado."
                        print(msg)
                        logging.critical(msg.replace("[DISCONNECTED] ", ""))  # Guardar en logs sin corchetes
                        self.device_status[device["address"]] = False  # Marcar como desconectado

                    msg = f"[WARNING] {device['name']} no encontrado. Reintentando en 10 segundos..."
                    print(msg)
                    logging.warning(msg.replace("[WARNING] ", ""))  # Guardar en logs sin corchetes
                    await asyncio.sleep(10)  # Esperar 10 segundos antes de reintentar
                    continue  # Continuar buscando el dispositivo

                msg = f"[INFO] Intentando conectar a {device['name']}..."
                print(msg)
                logging.info(msg.replace("[INFO] ", ""))

                async with BleakClient(device["address"]) as client:
                    if client.is_connected:
                        self.device_status[device["address"]] = True  # Marcar como conectado
                        msg = f"[CONNECTED] ✅ Conectado a {device['name']}"
                        print(msg)
                        logging.info(msg.replace("[CONNECTED] ✅ ", ""))

                        try:
                            await client.pair(protection_level=2)  # Intentar cifrar la conexión
                            msg = f"[SECURE] 🔒 Conexión cifrada con {device['name']}"
                            print(msg)
                            logging.info(msg.replace("[SECURE] 🔒 ", ""))
                        except Exception as e:
                            msg = f"[WARNING] No se pudo cifrar la conexión: {e}"
                            print(msg)
                            logging.warning(msg.replace("[WARNING] ", ""))

                        # Manejo de notificaciones BLE
                        def notification_handler(sender, data):
                            decoded_data = data.decode('utf-8')  # Convertir datos BLE en texto legible

                            # Filtrar mensajes de datos (No guardarlos en logs, ya están en la BD)
                            if "[ALERT]" in decoded_data:
                                msg = f"[DATA] {device['name']}: {decoded_data}"
                                print(msg)  # Solo se muestra en consola, no en logs

                                try:
                                    # Extraer los valores clave del mensaje recibido
                                    partes = decoded_data.split(" | ")
                                    spoofed_bssid = partes[1].split(": ")[1].strip()
                                    target_mac = partes[2].split(": ")[1].strip()
                                    bssid = partes[3].split(": ")[1].strip()
                                    canal = int(partes[4].split(": ")[1].strip())
                                    nodo_iot = device['name']

                                    # Guardar en la base de datos
                                    guardar_alerta(nodo_iot, spoofed_bssid, target_mac, bssid, canal)

                                except Exception as e:
                                    msg = f"[ERROR] Error al procesar los datos BLE: {e}"
                                    print(msg)
                                    logging.error(msg.replace("[ERROR] ", ""))  # Guardar error en logs sin corchetes

                        await client.start_notify(self.characteristic_uuid, notification_handler)
                        msg = f"[INFO] Esperando datos de {device['name']}..."
                        print(msg)
                        logging.info(msg.replace("[INFO] ", ""))

                        while client.is_connected:
                            await asyncio.sleep(1)

            except Exception as e:
                error_message = str(e)

                if "org.bluez.Error.InProgress" in error_message:
                    msg = "[ERROR] BlueZ ocupado. Esperando 10 segundos antes de reintentar..."
                    print(msg)
                    logging.error(msg.replace("[ERROR] ", ""))
                    await asyncio.sleep(10)
                elif "Characteristic" in error_message:
                    msg = f"[ERROR] Error con {device['name']}: No se pudo acceder a la característica."
                    print(msg)
                    logging.error(msg.replace("[ERROR] ", ""))
                else:
                    msg = f"[ERROR] Error con {device['name']}: {error_message}"
                    print(msg)
                    logging.error(msg.replace("[ERROR] ", ""))

                msg = f"[DISCONNECTED] Reintentando conexión con {device['name']} en 10 segundos..."
                print(msg)
                logging.info(msg.replace("[DISCONNECTED] ", ""))
                await asyncio.sleep(10)

    async def run(self):
        """Ejecuta la conexión a los dispositivos en paralelo, evitando bloqueos."""
        tasks = [asyncio.create_task(self.handle_device(device)) for device in self.devices]
        await asyncio.gather(*tasks)  # Procesar dispositivos en paralelo
