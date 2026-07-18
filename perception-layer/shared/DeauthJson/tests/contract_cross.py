#!/usr/bin/env python3
"""
Cruce de contrato C -> Python (F5-1).

Ejecuta el binario ``emit_vectors`` (que serializa vectores VALIDOS con
``deauth_json.c``) y verifica que el parser REAL ``parse_event`` de
``processing-layer/src/ble_manager.py`` los ACEPTA y NORMALIZA correctamente.

Solo se cruzan vectores validos producidos por C: los rechazos del serializador se
prueban en ``test_deauth_json.c`` y los rechazos de JSON arbitrario por el parser
estan cubiertos por los tests F3. Aqui NO se fabrica JSON invalido a mano.

Bootstrap de stubs identico a ``processing-layer/tests/test_ble_manager.py``:
``ble_manager`` importa ``src.data_processor`` -> ``src.mqtt_client`` (que puede hacer
``exit(1)`` al importar), asi que se stubean los servicios externos ANTES del import.
Solo se usa la biblioteca estandar; no hay conexiones reales.
"""
import json
import os
import subprocess
import sys
from unittest.mock import MagicMock

# --- Localizar processing-layer (repo raiz = 4 niveles sobre tests/). ---
_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.abspath(os.path.join(_HERE, "..", "..", "..", ".."))
_PROC = os.path.join(_REPO, "processing-layer")
sys.path.insert(0, _PROC)

# --- Entorno minimo + stubs de dependencias pesadas antes del import. ---
# Se stubea tambien ``src.data_processor`` (que importa ``requests`` y ``src.mqtt_client``):
# ``parse_event`` NO lo usa, asi que el contrato queda autocontenido con solo la stdlib,
# sin depender de ``requests`` ni de pip en el runner de CI. La fidelidad se mantiene:
# el ``parse_event`` que se cruza es el real de ``ble_manager``.
os.environ.setdefault("BACKEND_URL", "http://backend.test")
for _mod in (
    "bleak",
    "src.data_processor",
    "src.database",
    "src.mqtt_client",
    "src.telegram_alert",
    "src.logs_config.logger_config",
):
    sys.modules.setdefault(_mod, MagicMock())

from src.ble_manager import parse_event  # noqa: E402  (import tras configurar stubs)

_SUBTYPE_EVENT = {12: "deauth", 10: "disassoc"}


def main():
    if len(sys.argv) != 2:
        print("uso: contract_cross.py <ruta_emit_vectors>", file=sys.stderr)
        return 2

    proc = subprocess.run([sys.argv[1]], capture_output=True, text=True)
    if proc.returncode != 0:
        print("emit_vectors fallo (rc=%d): %s" % (proc.returncode, proc.stderr.strip()), file=sys.stderr)
        return 1

    lines = [ln for ln in proc.stdout.splitlines() if ln.strip()]
    if not lines:
        print("emit_vectors no produjo vectores", file=sys.stderr)
        return 1

    fail = 0
    for i, ln in enumerate(lines, 1):
        # Cada linea trae GROUND-TRUTH independiente (calculado por emit_vectors desde la
        # ENTRADA, NO desde el JSON) + el JSON emitido:
        #   <expected_node>\t<event_type>\t<s>\t<d>\t<b>\t<c>\t<json>
        cols = ln.split("\t")
        if len(cols) != 7:
            print("  vector %d: se esperaban 7 columnas, hay %d" % (i, len(cols)), file=sys.stderr)
            fail += 1
            continue
        expected_node, gt_event, gt_s, gt_d, gt_b, gt_c, payload = cols

        # 1) El JSON emitido por C debe ser JSON valido y empezar por '{'.
        if not payload.startswith("{"):
            print("  vector %d: el payload no empieza por '{': %r" % (i, payload), file=sys.stderr)
            fail += 1
            continue
        try:
            obj = json.loads(payload)
        except ValueError as exc:
            print("  vector %d: JSON invalido (%s): %s" % (i, exc, payload), file=sys.stderr)
            fail += 1
            continue

        # 2) Verificacion DIRECTA del serializador contra el ground-truth (independiente
        #    del parser): mapeo DT-24 src->s, dst->d, bssid->b, con MAC DISTINTAS por campo.
        errores = []
        if obj.get("v") != 1:
            errores.append("v=%r != 1" % obj.get("v"))
        if obj.get("s") != gt_s:
            errores.append("s=%r != src esperado %r (posible swap s/d/b)" % (obj.get("s"), gt_s))
        if obj.get("d") != gt_d:
            errores.append("d=%r != dst esperado %r (posible swap s/d/b)" % (obj.get("d"), gt_d))
        if obj.get("b") != gt_b:
            errores.append("b=%r != bssid esperado %r (posible swap s/d/b)" % (obj.get("b"), gt_b))
        if obj.get("c") != int(gt_c):
            errores.append("c=%r != canal esperado %s" % (obj.get("c"), gt_c))
        if _SUBTYPE_EVENT.get(obj.get("e")) != gt_event:
            errores.append("e=%r no mapea a %r" % (obj.get("e"), gt_event))
        if errores:
            print("  vector %d: JSON del serializador no coincide con ground-truth: %s"
                  % (i, "; ".join(errores)), file=sys.stderr)
            fail += 1
            continue

        # 3) El parser REAL debe ACEPTAR y NORMALIZAR al GROUND-TRUTH (no al JSON releido).
        result = parse_event(payload, expected_node)
        if result is None:
            print("  vector %d: parse_event DESCARTO un vector valido: %s" % (i, payload), file=sys.stderr)
            fail += 1
            continue
        esperado = {
            "nodo_iot": expected_node,   # identidad autoritativa, NO el "n" del payload
            "spoofed_bssid": gt_s,       # src
            "target_mac": gt_d,          # dst
            "bssid": gt_b,               # bssid
            "canal": int(gt_c),
            "event_type": gt_event,
        }
        if result != esperado:
            print("  vector %d: normalizacion inesperada\n    esperado=%s\n    obtenido=%s"
                  % (i, esperado, result), file=sys.stderr)
            fail += 1
            continue

        print("  vector %d OK: e=%s payload_n=%s expected_node=%s | s=%s d=%s b=%s -> %s"
              % (i, obj["e"], obj["n"], expected_node, gt_s, gt_d, gt_b, result["event_type"]))

    if fail:
        print("CONTRATO C->Python: %d de %d vector(es) fallaron" % (fail, len(lines)), file=sys.stderr)
        return 1
    print("CONTRATO C->Python: %d vectores aceptados y normalizados por el parse_event real" % len(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
