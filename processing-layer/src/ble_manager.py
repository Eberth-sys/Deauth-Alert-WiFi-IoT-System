# src/ble_manager.py

# -------------------- Importaciones --------------------
from bleak import BleakClient, BleakScanner                              # Librería para manejar dispositivos Bluetooth Low Energy (BLE)
import asyncio                                                           # Para ejecutar tareas asíncronas
import json                                                             # Para parsear el contrato de evento en formato JSON (DEC-0003)
import re                                                               # Para validar el formato de direcciones MAC/BSSID
from src.data_processor import guardar_alerta, actualizar_estado_esp32   # Funciones para manejar alertas y estados
from src.logs_config.logger_config import logger                         # Logger configurado para registrar eventos

# -------------------- Parser dual de eventos BLE (DEC-0003) --------------------
# La RPi acepta dos formatos por compatibilidad transicional:
#   1) JSON (contrato v1): {"v":1,"e":<subtipo>,"n":<nodo>,"s":<src>,"d":<dst>,"b":<bssid>,"c":<canal>}
#   2) Legacy de texto (firmware actual): "[ALERT] ... | Origen: .. | Destino: .. | BSSID: .. | Canal: .."
# El firmware JSON se incorpora en F5; hasta entonces conviven ambos.

# Subtipo de management frame 802.11 (campo "e") -> event_type persistido.
#   12 (0x0C) -> deauth   |   10 (0x0A) -> disassoc
_SUBTYPE_TO_EVENT = {12: "deauth", 10: "disassoc"}

# event_type por defecto del formato legacy (no transporta el tipo explícito).
_LEGACY_EVENT_TYPE = "deauth"

# Campos obligatorios del contrato JSON v1 (DEC-0003).
_JSON_REQUIRED_KEYS = ("v", "e", "n", "s", "d", "b", "c")

# Validación estricta de direcciones MAC/BSSID (XX:XX:XX:XX:XX:XX).
_MAC_RE = re.compile(r"^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$")

# Largo máximo razonable para el identificador de nodo del payload ("n").
_MAX_NODE_LEN = 64


def _parse_json_event(text, expected_node):
    """
    Valida y normaliza un evento en formato JSON (contrato v1, DEC-0003).
    Devuelve un dict de alerta normalizada o None si debe descartarse (D-7).
    No lanza excepción.
    """
    try:
        payload = json.loads(text)
    except (ValueError, TypeError):
        logger.warning("Evento JSON malformado; se descarta (D-7).")
        return None

    if not isinstance(payload, dict):
        logger.warning("Evento JSON no es un objeto; se descarta (D-7).")
        return None

    # Versión de contrato: exclusivamente v == 1 (entero, no booleano).
    v = payload.get("v")
    if isinstance(v, bool) or not isinstance(v, int) or v != 1:
        logger.warning("Versión de contrato no admitida (v=%r); se descarta (D-7).", v)
        return None

    # Campos obligatorios: deben estar presentes todos los del contrato. Se aceptan
    # campos adicionales para permitir una evolución compatible del esquema (no se rechazan).
    faltantes = [k for k in _JSON_REQUIRED_KEYS if k not in payload]
    if faltantes:
        logger.warning("Evento JSON con campos faltantes %s; se descarta (D-7).", faltantes)
        return None

    # Subtipo 802.11 -> event_type (entero, no booleano; solo deauth/disassoc).
    e = payload.get("e")
    if isinstance(e, bool) or not isinstance(e, int):
        logger.warning("Subtipo de evento con tipo inválido (e=%r); se descarta (D-7).", e)
        return None
    event_type = _SUBTYPE_TO_EVENT.get(e)
    if event_type is None:
        logger.warning("Subtipo de evento no admitido (e=%r); se descarta (D-7).", e)
        return None

    # Campo "n": identificador de nodo del payload. Debe existir, ser string no
    # vacío y de largo razonable. NO se usa para atribuir nodo_iot (ver abajo).
    n = payload.get("n")
    if not isinstance(n, str) or not n.strip() or len(n) > _MAX_NODE_LEN:
        logger.warning("Campo 'n' inválido; se descarta (D-7).")
        return None

    # Direcciones src/dst/bssid: formato MAC estricto.
    s = payload.get("s")
    d = payload.get("d")
    b = payload.get("b")
    for etiqueta, valor in (("s", s), ("d", d), ("b", b)):
        if not isinstance(valor, str) or not _MAC_RE.match(valor):
            logger.warning("Campo '%s' con formato MAC inválido; se descarta (D-7).", etiqueta)
            return None

    # Canal: entero en rango 802.11 2.4 GHz (1..14). bool es subclase de int -> excluir.
    c = payload.get("c")
    if isinstance(c, bool) or not isinstance(c, int) or not (1 <= c <= 14):
        logger.warning("Canal fuera de rango o inválido (c=%r); se descarta (D-7).", c)
        return None

    # -------------------- Identidad de nodo (Opción A, transitoria) --------------------
    # La identidad AUTORITATIVA operativa es expected_node (device['name'] de la
    # config + conexión BLE activa). El campo "n" del payload NO se usa para atribuir
    # nodo_iot y una discrepancia NO descarta el evento.
    # NOTA (transitoria, F5): hoy el DEVICE_NAME del firmware (p.ej.
    # "ESP32_01_Deauth_Detector_CH_01") difiere del node_id de devices.yaml (p.ej.
    # "ESP32_1_CH_01"). En F5 el firmware deberá emitir un node_id canónico igual al
    # de la config; el nombre BLE visible puede permanecer separado. Hasta entonces la
    # discrepancia se registra a nivel debug (sin saturar logs) y se conserva la
    # identidad de la conexión.
    if expected_node is not None and n != expected_node:
        logger.debug(
            "Discrepancia de nodo (n=%r, esperado=%r); se conserva la identidad de conexión.",
            n, expected_node,
        )

    return {
        "nodo_iot": expected_node if expected_node is not None else n,
        "spoofed_bssid": s,   # Origen (AP suplantada)
        "target_mac": d,      # Destino (cliente objetivo)
        "bssid": b,           # BSSID de la red
        "canal": c,
        "event_type": event_type,
    }


def _parse_legacy_event(text, expected_node):
    """
    Parsea el formato legacy de texto del firmware actual:
    "[ALERT] ... | Origen: <src> | Destino: <dst> | BSSID: <bssid> | Canal: <ch>".
    Devuelve un dict de alerta normalizada o None. event_type por defecto: 'deauth'.
    No lanza excepción.
    """
    try:
        partes = text.split(" | ")
        spoofed_bssid = partes[1].split(": ")[1].strip()
        target_mac = partes[2].split(": ")[1].strip()
        bssid = partes[3].split(": ")[1].strip()
        canal = int(partes[4].split(": ")[1].strip())
    except (IndexError, ValueError) as e:
        logger.error("Error al procesar alerta legacy: %s", e)
        return None

    return {
        "nodo_iot": expected_node,
        "spoofed_bssid": spoofed_bssid,
        "target_mac": target_mac,
        "bssid": bssid,
        "canal": canal,
        "event_type": _LEGACY_EVENT_TYPE,
    }


def parse_event(raw_message, expected_node):
    """
    Parser dual de eventos recibidos por BLE (DEC-0003).

    - Aplica strip() antes de decidir el formato.
    - Si el mensaje empieza con '{': formato JSON (contrato v1, validación estricta).
    - Si contiene '[ALERT]': formato legacy de texto (event_type='deauth').
    - En cualquier otro caso: no es una alerta reconocible -> None (sin error).

    Devuelve un dict de alerta normalizada o None. NUNCA lanza excepción, para no
    interrumpir notification_handler.

    :param raw_message: str ya decodificado desde BLE (o None).
    :param expected_node: identidad operativa del nodo (device['name']).
    """
    try:
        if not isinstance(raw_message, str):
            return None
        text = raw_message.strip()
        if not text:
            return None
        if text.startswith("{"):
            return _parse_json_event(text, expected_node)
        if "[ALERT]" in text:
            return _parse_legacy_event(text, expected_node)
        # No es una alerta reconocible (p.ej. mensajes de estado): se ignora en silencio.
        return None
    except Exception as e:  # Cinturón de seguridad: jamás propagar hacia el callback BLE.
        logger.error("Error inesperado al parsear evento BLE: %s", e)
        return None


# -------------------- Clase: Gestor de Dispositivos BLE --------------------
class BLEManager:
    def __init__(self, devices, service_uuid, characteristic_uuid):
        """
        Inicializa el gestor de dispositivos BLE.
        :param devices: Lista de dispositivos ESP32 configurados.
        :param service_uuid: UUID del servicio BLE.
        :param characteristic_uuid: UUID de la característica BLE.
        """
        self.devices = devices
        self.service_uuid = service_uuid
        self.characteristic_uuid = characteristic_uuid
        self.device_status = {device["address"]: False for device in devices}  # Estado actual de cada dispositivo

    async def handle_device(self, device):
        """
        Gestiona la conexión, monitoreo y recepción de datos de un dispositivo BLE.
        """
        while True:
            try:
                await BleakScanner.discover(timeout=1)  # Escanear dispositivos BLE

                msg = f"[INFO] Buscando {device['name']} ({device['address']})..."
                print(msg)
                logger.info(msg.replace("[INFO] ", ""))

                found_device = await BleakScanner.find_device_by_address(device["address"], timeout=10)

                if not found_device:
                    # Dispositivo no encontrado
                    msg = f"[DISCONNECTED] {device['name']} se ha desconectado."
                    print(msg)
                    logger.critical(msg.replace("[DISCONNECTED] ", ""))

                    actualizar_estado_esp32(device["name"], device["address"], "disconnected")
                    self.device_status[device["address"]] = False

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
                        actualizar_estado_esp32(device["name"], device["address"], "connected")

                        try:
                            await client.pair(protection_level=2)  # Intentar conexión cifrada
                            msg = f"[SECURE] 🔒 Conexión cifrada con {device['name']}"
                            print(msg)
                            logger.info(msg.replace("[SECURE] 🔒 ", ""))
                        except Exception as e:
                            msg = f"[WARNING] No se pudo cifrar la conexión: {e}"
                            print(msg)
                            logger.warning(msg.replace("[WARNING] ", ""))

                        def notification_handler(sender, data):
                            """
                            Callback para datos recibidos por BLE. Aplica el parser dual
                            (DEC-0003): JSON (contrato v1) o legacy de texto. No propaga
                            excepciones para no interrumpir la recepción.
                            """
                            try:
                                decoded_data = data.decode("utf-8")
                            except (UnicodeDecodeError, AttributeError) as e:
                                logger.error("No se pudo decodificar el dato BLE: %s", e)
                                return

                            # device['name'] es la identidad operativa autoritativa del nodo
                            # (proviene de la config y de la conexión BLE activa).
                            alerta = parse_event(decoded_data, device["name"])
                            if alerta is None:
                                return

                            msg = f"[DATA] {device['name']}: {decoded_data}"
                            print(msg)

                            try:
                                guardar_alerta(
                                    nodo_iot=alerta["nodo_iot"],
                                    spoofed_bssid=alerta["spoofed_bssid"],
                                    bssid=alerta["bssid"],
                                    target_mac=alerta["target_mac"],
                                    canal=alerta["canal"],
                                    event_type=alerta["event_type"],
                                )
                            except Exception as e:
                                msg = f"[ERROR] Error al guardar la alerta BLE: {e}"
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
                actualizar_estado_esp32(device["name"], device["address"], "disconnected")
                await asyncio.sleep(10)

    async def run(self):
        """
        Ejecuta la gestión de dispositivos BLE en paralelo.
        """
        tasks = [asyncio.create_task(self.handle_device(device)) for device in self.devices]
        await asyncio.gather(*tasks)
