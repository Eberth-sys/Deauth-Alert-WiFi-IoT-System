# processing-layer/tests/test_ble_manager.py
"""
Tests del parser dual de eventos BLE (F3, DEC-0003).

Se valida la función pura ``parse_event``:
- Formato JSON (contrato v1) con validación estricta y descarte D-7.
- Formato legacy de texto del firmware actual (event_type='deauth' por defecto).
- Identidad de nodo (Opción A): expected_node es autoritativo; una diferencia en
  el campo "n" NO descarta el evento y NO cambia nodo_iot.
- Robustez: parse_event nunca propaga excepciones.

Bootstrap de stubs (DEUDA TÉCNICA):
``ble_manager`` importa ``src.data_processor`` en el nivel de módulo, que a su vez
importa ``src.mqtt_client``. Ese módulo se CONECTA a AWS IoT y puede ejecutar
``exit(1)`` durante el import. Por eso se stubean los servicios externos ANTES de
importar ``ble_manager``. Ningún test realiza conexiones reales a AWS, Telegram ni
PostgreSQL. Hacer ``mqtt_client`` seguro al importar queda para una rama aparte.
"""
import json
import os
import sys
from unittest.mock import MagicMock

# --- Entorno mínimo: data_processor hace raise si falta BACKEND_URL en el import. ---
os.environ.setdefault("BACKEND_URL", "http://backend.test")

# --- Stubs de dependencias pesadas / servicios externos antes del import. ---
for _mod in (
    "bleak",
    "src.database",
    "src.mqtt_client",
    "src.telegram_alert",
    "src.logs_config.logger_config",
):
    sys.modules.setdefault(_mod, MagicMock())

from src.ble_manager import parse_event  # noqa: E402  (import tras configurar stubs)

NODO = "ESP32_1_CH_01"


def _json_evento(**overrides):
    """Construye un payload JSON válido del contrato v1, con overrides opcionales."""
    base = {
        "v": 1,
        "e": 12,
        "n": NODO,
        "s": "AA:BB:CC:DD:EE:01",
        "d": "11:22:33:44:55:66",
        "b": "AA:BB:CC:DD:EE:FF",
        "c": 6,
    }
    base.update(overrides)
    return json.dumps(base)


# ----------------------------- JSON válido -----------------------------
def test_json_deauth_valido():
    r = parse_event(_json_evento(e=12), NODO)
    assert r is not None
    assert r["event_type"] == "deauth"
    assert r["nodo_iot"] == NODO
    assert r["spoofed_bssid"] == "AA:BB:CC:DD:EE:01"   # Origen (s)
    assert r["target_mac"] == "11:22:33:44:55:66"      # Destino (d)
    assert r["bssid"] == "AA:BB:CC:DD:EE:FF"           # BSSID (b)
    assert r["canal"] == 6


def test_json_disassoc_valido():
    r = parse_event(_json_evento(e=10), NODO)
    assert r is not None
    assert r["event_type"] == "disassoc"


def test_json_con_espacios_y_salto_de_linea():
    r = parse_event("  " + _json_evento() + "\n", NODO)
    assert r is not None
    assert r["event_type"] == "deauth"


# --------------------- Identidad de nodo (Opción A) ---------------------
def test_json_n_distinto_no_descarta_y_usa_expected():
    # El DEVICE_NAME del firmware difiere del node_id de config: NO se descarta;
    # nodo_iot se atribuye a expected_node (identidad de conexión).
    r = parse_event(_json_evento(n="ESP32_01_Deauth_Detector_CH_01"), NODO)
    assert r is not None
    assert r["nodo_iot"] == NODO


def test_json_n_vacio_descarta():
    assert parse_event(_json_evento(n=""), NODO) is None
    assert parse_event(_json_evento(n="   "), NODO) is None


def test_json_n_no_string_descarta():
    assert parse_event(_json_evento(n=123), NODO) is None


def test_json_n_demasiado_largo_descarta():
    assert parse_event(_json_evento(n="X" * 65), NODO) is None


# ----------------- D-7: versión / subtipo / estructura -----------------
def test_json_version_no_admitida_descarta():
    assert parse_event(_json_evento(v=2), NODO) is None
    assert parse_event(_json_evento(v="1"), NODO) is None
    assert parse_event(_json_evento(v=True), NODO) is None


def test_json_subtipo_desconocido_descarta():
    assert parse_event(_json_evento(e=11), NODO) is None    # ni deauth ni disassoc
    assert parse_event(_json_evento(e="12"), NODO) is None  # tipo inválido


def test_json_campo_faltante_descarta():
    d = {
        "v": 1, "e": 12, "n": NODO,
        "s": "AA:BB:CC:DD:EE:01", "d": "11:22:33:44:55:66",
        "b": "AA:BB:CC:DD:EE:FF",  # falta 'c'
    }
    assert parse_event(json.dumps(d), NODO) is None


def test_json_malformado_descarta():
    assert parse_event('{"v":1, "e":12,', NODO) is None


def test_json_no_objeto_descarta():
    assert parse_event("[1, 2, 3]", NODO) is None


# --------------------- Validación de campos ---------------------
def test_json_mac_invalida_descarta():
    assert parse_event(_json_evento(d="no-es-mac"), NODO) is None
    assert parse_event(_json_evento(s="AA:BB:CC:DD:EE"), NODO) is None        # incompleta
    assert parse_event(_json_evento(b="AA:BB:CC:DD:EE:FF:00"), NODO) is None  # de más


def test_json_canal_fuera_de_rango_descarta():
    assert parse_event(_json_evento(c=0), NODO) is None
    assert parse_event(_json_evento(c=15), NODO) is None
    assert parse_event(_json_evento(c="6"), NODO) is None


def test_json_canal_booleano_descarta():
    assert parse_event(_json_evento(c=True), NODO) is None


# ----------------------------- Legacy -----------------------------
def test_legacy_valido_default_deauth():
    # Formato real del firmware actual (main.ino):
    txt = ("[ALERT] Ataque de Deauthentication detectado | "
           "Origen: AA:BB:CC:DD:EE:01 | Destino: 11:22:33:44:55:66 | "
           "BSSID: AA:BB:CC:DD:EE:FF | Canal: 6")
    r = parse_event(txt, NODO)
    assert r is not None
    assert r["event_type"] == "deauth"          # default legacy
    assert r["nodo_iot"] == NODO
    assert r["spoofed_bssid"] == "AA:BB:CC:DD:EE:01"
    assert r["target_mac"] == "11:22:33:44:55:66"
    assert r["bssid"] == "AA:BB:CC:DD:EE:FF"
    assert r["canal"] == 6


def test_legacy_malformado_descarta():
    assert parse_event("[ALERT] | incompleto", NODO) is None


# ----------------------- No-alerta / robustez -----------------------
def test_texto_no_alerta_devuelve_none():
    assert parse_event("mensaje de estado cualquiera", NODO) is None


def test_none_devuelve_none_sin_excepcion():
    assert parse_event(None, NODO) is None


def test_bytes_no_string_devuelve_none():
    # parse_event espera str ya decodificado; bytes -> None sin excepción.
    assert parse_event(b"{}", NODO) is None


def test_vacio_devuelve_none():
    assert parse_event("   ", NODO) is None
    assert parse_event("", NODO) is None
