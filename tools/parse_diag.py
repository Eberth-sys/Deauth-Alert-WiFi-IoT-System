#!/usr/bin/env python3
"""Parser de las lineas diagnosticas [DIAG] de DeauthDiag (Fase 8 / F6a-1).

Solo biblioteca estandar: sin PyYAML ni jsonschema. El contrato que valida es el
mismo que documenta docs/lab/diag-schema.json (la paridad se verifica en tests).

Reglas:
  * las lineas que NO empiezan con "[DIAG] " se ignoran en silencio (un log de
    consola mezcla arranque, warnings y alertas JSON v1);
  * cualquier linea "[DIAG] " malformada se rechaza indicando el NUMERO de linea
    y el motivo, y el proceso termina con codigo != 0;
  * se exigen EXACTAMENTE las 15 claves (ni faltantes, ni adicionales, ni duplicadas);
  * los enteros se validan con `type(v) is int` para NO aceptar booleanos
    (en Python `isinstance(True, int)` es verdadero);
  * la salida es determinista y sanitizada: se reconstruye desde los valores ya
    validados, nunca se copia la linea cruda de entrada;
  * comportamiento FAIL-CLOSED: si hay al menos una linea [DIAG] invalida se
    reportan todos los errores y NO se genera salida (no se abre, crea ni
    sobrescribe el destino), para no dejar evidencia parcial que parezca completa.

Uso:
    python3 parse_diag.py serial.log [--format csv|jsonl] [--output out.csv]
    cat serial.log | python3 parse_diag.py - --format jsonl
"""

import argparse
import json
import re
import sys

PREFIX = "[DIAG] "

DIAG_V = 1
NODE_ID_MAX_LEN = 64
NODE_ID_RE = re.compile(r"^[A-Za-z0-9_-]+$")

U16_MAX = 65535
U32_MAX = 4294967295
U64_MAX = 18446744073709551615

# Campos enteros -> (minimo, maximo). Derivados de los tipos reales de
# deauth_diag_state_t / deauth_diag_delta_t (uint16/uint32/uint64).
INT_FIELDS = {
    "up_ms": (0, U64_MAX),
    "stack_min_free_bytes": (0, U32_MAX),
    "queue_max_depth": (0, U16_MAX),
    "heap_min_free_bytes": (0, U32_MAX),
    "mtu_negotiated": (0, U16_MAX),
    "d_dropped_events": (0, U32_MAX),
    "d_dropped_mtu": (0, U32_MAX),
    "d_rl_suppressed": (0, U32_MAX),
    "d_rl_fail_open": (0, U32_MAX),
    "t_dropped_events": (0, U64_MAX),
    "t_dropped_mtu": (0, U64_MAX),
    "t_rl_suppressed": (0, U64_MAX),
    "t_rl_fail_open": (0, U64_MAX),
}

# Orden FIJO de columnas/claves de salida = orden del contrato emitido por el firmware.
FIELD_ORDER = (
    "diag_v",
    "n",
    "up_ms",
    "stack_min_free_bytes",
    "queue_max_depth",
    "heap_min_free_bytes",
    "mtu_negotiated",
    "d_dropped_events",
    "d_dropped_mtu",
    "d_rl_suppressed",
    "d_rl_fail_open",
    "t_dropped_events",
    "t_dropped_mtu",
    "t_rl_suppressed",
    "t_rl_fail_open",
)
REQUIRED_KEYS = frozenset(FIELD_ORDER)


class DiagError(Exception):
    """Linea [DIAG] invalida. El mensaje NUNCA incluye la linea cruda."""


def _pairs_hook(pairs):
    """Detecta claves duplicadas, que json.loads aceptaria quedandose con la ultima."""
    seen = set()
    for key, _value in pairs:
        if key in seen:
            raise DiagError("clave duplicada: %s" % key)
        seen.add(key)
    return dict(pairs)


def parse_payload(payload):
    """Valida la carga JSON de una linea [DIAG] y devuelve un dict normalizado."""
    try:
        obj = json.loads(payload, object_pairs_hook=_pairs_hook)
    except DiagError:
        raise
    except ValueError as exc:
        raise DiagError("JSON invalido (%s)" % type(exc).__name__)

    if not isinstance(obj, dict):
        raise DiagError("la carga no es un objeto JSON")

    keys = set(obj)
    faltantes = sorted(REQUIRED_KEYS - keys)
    if faltantes:
        raise DiagError("claves faltantes: %s" % ", ".join(faltantes))
    sobrantes = sorted(keys - REQUIRED_KEYS)
    if sobrantes:
        raise DiagError("claves no permitidas: %s" % ", ".join(sobrantes))

    # diag_v: entero estricto e igual a la version soportada.
    version = obj["diag_v"]
    if type(version) is not int:
        raise DiagError("diag_v no es entero")
    if version != DIAG_V:
        raise DiagError("diag_v no soportado: %d (se espera %d)" % (version, DIAG_V))

    # node_id: cadena acotada y con alfabeto restringido.
    node = obj["n"]
    if not isinstance(node, str):
        raise DiagError("n no es cadena")
    if not 1 <= len(node) <= NODE_ID_MAX_LEN:
        raise DiagError("n fuera de rango de longitud (%d)" % len(node))
    # fullmatch (no match): con match() el ancla '$' aceptaria un salto de linea final.
    if not NODE_ID_RE.fullmatch(node):
        raise DiagError("n con caracteres no permitidos")

    for campo in sorted(INT_FIELDS):
        minimo, maximo = INT_FIELDS[campo]
        valor = obj[campo]
        # `type(v) is int` rechaza bool, que en Python es subclase de int.
        if type(valor) is not int:
            raise DiagError("%s no es entero" % campo)
        if not minimo <= valor <= maximo:
            raise DiagError("%s fuera de rango: %d" % (campo, valor))

    return {campo: obj[campo] for campo in FIELD_ORDER}


def parse_lines(lineas):
    """Recorre un iterable de lineas. Devuelve (registros, errores).

    errores es una lista de (numero_de_linea, motivo); nunca contiene texto crudo.
    """
    registros = []
    errores = []
    for numero, linea in enumerate(lineas, start=1):
        texto = linea.rstrip("\n").rstrip("\r")
        if not texto.startswith(PREFIX):
            continue                      # linea ajena al diagnostico: se ignora
        try:
            registros.append(parse_payload(texto[len(PREFIX):]))
        except DiagError as exc:
            errores.append((numero, str(exc)))
    return registros, errores


def escribir_csv(registros, salida):
    salida.write(",".join(FIELD_ORDER) + "\n")
    for reg in registros:
        salida.write(",".join(str(reg[c]) for c in FIELD_ORDER) + "\n")


def escribir_jsonl(registros, salida):
    for reg in registros:
        # sort_keys + separadores fijos => salida byte a byte determinista.
        salida.write(json.dumps(reg, sort_keys=True, separators=(",", ":")) + "\n")


def main(argv=None):
    ap = argparse.ArgumentParser(description="Parsea lineas [DIAG] de un log de consola serie.")
    ap.add_argument("entrada", help="archivo de log, o '-' para stdin")
    ap.add_argument("--format", choices=("csv", "jsonl"), default="csv",
                    help="formato de salida (por defecto: csv)")
    ap.add_argument("--output", default="-", help="archivo de salida, o '-' para stdout")
    args = ap.parse_args(argv)

    if args.entrada == "-":
        registros, errores = parse_lines(sys.stdin)
    else:
        try:
            with open(args.entrada, "r", encoding="utf-8", errors="replace") as fh:
                registros, errores = parse_lines(fh)
        except OSError as exc:
            sys.stderr.write("error: no se pudo leer %s (%s)\n" % (args.entrada, exc.strerror))
            return 2

    for numero, motivo in errores:
        sys.stderr.write("error: linea %d: %s\n" % (numero, motivo))

    # FAIL-CLOSED: ante cualquier linea [DIAG] invalida no se emite nada y no se
    # toca el destino (ni se crea ni se sobrescribe un archivo previo).
    if errores:
        sys.stderr.write(
            "resumen: %d linea(s) [DIAG] validas, %d rechazada(s); fail-closed: "
            "no se genera ni se sobrescribe la salida\n" % (len(registros), len(errores)))
        return 1

    if args.output == "-":
        destino = sys.stdout
        cerrar = False
    else:
        try:
            destino = open(args.output, "w", encoding="utf-8", newline="\n")
        except OSError as exc:
            sys.stderr.write("error: no se pudo escribir %s (%s)\n" % (args.output, exc.strerror))
            return 2
        cerrar = True
    try:
        if args.format == "csv":
            escribir_csv(registros, destino)
        else:
            escribir_jsonl(registros, destino)
    finally:
        if cerrar:
            destino.close()

    sys.stderr.write("resumen: %d linea(s) [DIAG] validas, 0 rechazada(s)\n" % len(registros))
    return 0


if __name__ == "__main__":
    sys.exit(main())
