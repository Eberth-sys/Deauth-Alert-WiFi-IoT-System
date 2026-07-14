# processing-layer/tests/test_data_processor.py
"""
Tests de ``guardar_alerta`` (F3, DEC-0003) con mocks de servicios externos.

Se verifica que event_type se propaga a las tres salidas:
1. INSERT en PostgreSQL: el SQL nombra la columna event_type y el parámetro viaja
   en la posición correcta (incluida la compatibilidad legacy con default 'deauth').
2. alert_data publicado por MQTT (publish_alert) incluye event_type.
3. Mensaje de Telegram con etiqueta legible ("Desautenticación"/"Desasociación").

Ningún test realiza conexiones reales a PostgreSQL, AWS ni Telegram.

Bootstrap de stubs (DEUDA TÉCNICA):
``data_processor`` importa ``src.database``, ``src.mqtt_client`` y
``src.telegram_alert`` en el nivel de módulo. ``src.mqtt_client`` se CONECTA a AWS
IoT y puede ejecutar ``exit(1)`` durante el import. Por eso se stubean ANTES de
importar ``data_processor``. Hacer ``mqtt_client`` seguro al importar queda para una
rama aparte.
"""
import os
import sys
from unittest.mock import MagicMock

import pytest

# --- Entorno mínimo: data_processor hace raise si falta BACKEND_URL en el import. ---
os.environ.setdefault("BACKEND_URL", "http://backend.test")

# --- Stubs de servicios externos antes del import. ---
for _mod in ("src.database", "src.mqtt_client", "src.telegram_alert"):
    sys.modules.setdefault(_mod, MagicMock())

import src.data_processor as dp  # noqa: E402  (import tras configurar stubs)


@pytest.fixture(autouse=True)
def reset_mocks():
    """Reinicia los mocks y el estado global de dedup antes de cada test."""
    cursor = MagicMock()
    conn = MagicMock()
    conn.cursor.return_value = cursor

    dp.get_db_connection.reset_mock()
    dp.get_db_connection.return_value = conn
    dp.publish_alert.reset_mock()
    dp.enviar_mensaje_telegram.reset_mock()

    # El filtro anti-duplicados es estado de módulo: limpiarlo evita interferencias.
    dp.alerta_reciente.clear()

    yield cursor, conn


def _llamar(reset_mocks, event_type=None, **kw):
    """Invoca guardar_alerta con datos base; sin event_type ejercita la ruta legacy."""
    args = dict(
        nodo_iot="ESP32_1_CH_01",
        spoofed_bssid="AA:BB:CC:DD:EE:01",
        bssid="AA:BB:CC:DD:EE:FF",
        target_mac="11:22:33:44:55:66",
        canal=6,
    )
    args.update(kw)
    if event_type is None:
        dp.guardar_alerta(**args)                     # ruta legacy: default 'deauth'
    else:
        dp.guardar_alerta(event_type=event_type, **args)


# ---------------- (1) Persistencia en BD ----------------
def test_insert_incluye_event_type_disassoc(reset_mocks):
    cursor, _ = reset_mocks
    _llamar(reset_mocks, event_type="disassoc")

    cursor.execute.assert_called_once()
    sql, params = cursor.execute.call_args[0]
    assert "event_type" in sql
    # Orden de columnas: (nodo_iot, spoofed_bssid, bssid, target_mac, canal, event_type)
    assert params[-1] == "disassoc"
    assert "disassoc" in params


def test_legacy_default_deauth_en_bd(reset_mocks):
    cursor, _ = reset_mocks
    _llamar(reset_mocks)  # sin event_type -> compatibilidad legacy

    sql, params = cursor.execute.call_args[0]
    assert params[-1] == "deauth"


# ---------------- (2) Publicación MQTT (AWS) ----------------
def test_publish_alert_incluye_event_type(reset_mocks):
    _llamar(reset_mocks, event_type="disassoc")

    dp.publish_alert.assert_called_once()
    alert_data = dp.publish_alert.call_args[0][0]
    assert alert_data["event_type"] == "disassoc"


def test_publish_alert_default_deauth(reset_mocks):
    _llamar(reset_mocks)

    alert_data = dp.publish_alert.call_args[0][0]
    assert alert_data["event_type"] == "deauth"


# ---------------- (3) Etiqueta legible en Telegram ----------------
def test_telegram_etiqueta_disassoc(reset_mocks):
    _llamar(reset_mocks, event_type="disassoc")

    dp.enviar_mensaje_telegram.assert_called_once()
    mensaje = dp.enviar_mensaje_telegram.call_args[0][0]
    assert "Desasociación" in mensaje


def test_telegram_etiqueta_deauth(reset_mocks):
    _llamar(reset_mocks, event_type="deauth")

    mensaje = dp.enviar_mensaje_telegram.call_args[0][0]
    assert "Desautenticación" in mensaje


# ---------------- Deduplicación por event_type ----------------
def test_deauth_y_disassoc_no_se_deduplican_entre_si(reset_mocks):
    # Mismo nodo/target/canal, distinto event_type dentro de la ventana de 30 s:
    # son eventos distintos y deben generar DOS notificaciones de Telegram.
    _llamar(reset_mocks, event_type="deauth")
    _llamar(reset_mocks, event_type="disassoc")

    assert dp.enviar_mensaje_telegram.call_count == 2
    etiquetas = " ".join(c.args[0] for c in dp.enviar_mensaje_telegram.call_args_list)
    assert "Desautenticación" in etiquetas
    assert "Desasociación" in etiquetas


def test_mismo_event_type_se_deduplica_en_ventana(reset_mocks):
    # Dos eventos idénticos (mismo event_type) dentro de la ventana: la segunda
    # notificación de Telegram se suprime por deduplicación.
    _llamar(reset_mocks, event_type="deauth")
    _llamar(reset_mocks, event_type="deauth")

    assert dp.enviar_mensaje_telegram.call_count == 1


# ---------------- (4) Sin conexiones reales ----------------
def test_no_hay_conexiones_reales(reset_mocks):
    # Las tres dependencias externas son mocks; nada toca AWS/Telegram/PostgreSQL.
    assert isinstance(dp.get_db_connection, MagicMock)
    assert isinstance(dp.publish_alert, MagicMock)
    assert isinstance(dp.enviar_mensaje_telegram, MagicMock)


def test_bd_no_disponible_no_publica_ni_notifica(reset_mocks):
    # Si no hay conexión a BD, no se publica MQTT ni se notifica a Telegram.
    dp.get_db_connection.return_value = None
    _llamar(reset_mocks, event_type="deauth")

    dp.publish_alert.assert_not_called()
    dp.enviar_mensaje_telegram.assert_not_called()
