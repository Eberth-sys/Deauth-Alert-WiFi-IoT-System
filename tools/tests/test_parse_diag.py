#!/usr/bin/env python3
"""Tests de parse_diag.py (Fase 8 / F6a-2). Solo biblioteca estandar.

Cubren: claves faltantes/adicionales/duplicadas, diag_v distinto de 1, booleanos
donde se esperan enteros, limites minimos y maximos, JSON malformado, log mixto
con lineas ajenas, paridad EXACTA parser <-> docs/lab/diag-schema.json, y salida
determinista que jamas copia contenido crudo de entrada.

Ejecucion:  python3 tools/tests/test_parse_diag.py
"""

import contextlib
import io
import json
import os
import sys
import tempfile
import unittest

_AQUI = os.path.dirname(os.path.abspath(__file__))
_TOOLS = os.path.dirname(_AQUI)
_RAIZ = os.path.dirname(_TOOLS)
if _TOOLS not in sys.path:
    sys.path.insert(0, _TOOLS)

import parse_diag  # noqa: E402

SCHEMA_PATH = os.path.join(_RAIZ, "docs", "lab", "diag-schema.json")

BASE = {
    "diag_v": 1,
    "n": "ESP32_1_CH_01",
    "up_ms": 123456,
    "stack_min_free_bytes": 2048,
    "queue_max_depth": 7,
    "heap_min_free_bytes": 98765,
    "mtu_negotiated": 247,
    "d_dropped_events": 0,
    "d_dropped_mtu": 0,
    "d_rl_suppressed": 12,
    "d_rl_fail_open": 0,
    "t_dropped_events": 3,
    "t_dropped_mtu": 0,
    "t_rl_suppressed": 140,
    "t_rl_fail_open": 2,
}


def linea(payload_dict=None, texto=None):
    """Construye una linea [DIAG] a partir de un dict o de texto crudo."""
    if texto is None:
        texto = json.dumps(payload_dict)
    return parse_diag.PREFIX + texto


class TestValido(unittest.TestCase):
    def test_linea_valida(self):
        reg = parse_diag.parse_payload(json.dumps(BASE))
        self.assertEqual(set(reg), set(parse_diag.FIELD_ORDER))
        self.assertEqual(reg["n"], "ESP32_1_CH_01")
        self.assertEqual(reg["t_rl_suppressed"], 140)

    def test_quince_claves(self):
        self.assertEqual(len(parse_diag.FIELD_ORDER), 15)
        self.assertEqual(len(parse_diag.REQUIRED_KEYS), 15)
        self.assertEqual(len(BASE), 15)


class TestClaves(unittest.TestCase):
    def test_clave_faltante(self):
        d = dict(BASE)
        del d["queue_max_depth"]
        with self.assertRaises(parse_diag.DiagError) as ctx:
            parse_diag.parse_payload(json.dumps(d))
        self.assertIn("faltantes", str(ctx.exception))
        self.assertIn("queue_max_depth", str(ctx.exception))

    def test_clave_adicional(self):
        d = dict(BASE)
        d["extra_no_permitida"] = 1
        with self.assertRaises(parse_diag.DiagError) as ctx:
            parse_diag.parse_payload(json.dumps(d))
        self.assertIn("no permitidas", str(ctx.exception))

    def test_clave_duplicada(self):
        # json.loads normalmente se queda con la ultima; el hook debe rechazarla.
        crudo = '{"diag_v":1,"diag_v":1,"n":"N1"}'
        with self.assertRaises(parse_diag.DiagError) as ctx:
            parse_diag.parse_payload(crudo)
        self.assertIn("duplicada", str(ctx.exception))


class TestVersion(unittest.TestCase):
    def test_diag_v_distinto(self):
        for v in (0, 2, 99):
            d = dict(BASE, diag_v=v)
            with self.assertRaises(parse_diag.DiagError) as ctx:
                parse_diag.parse_payload(json.dumps(d))
            self.assertIn("diag_v no soportado", str(ctx.exception))

    def test_diag_v_no_entero(self):
        d = dict(BASE, diag_v="1")
        with self.assertRaises(parse_diag.DiagError):
            parse_diag.parse_payload(json.dumps(d))


class TestBooleanos(unittest.TestCase):
    def test_bool_no_es_entero(self):
        # En Python isinstance(True, int) es True: el parser usa type(v) is int.
        for campo in ("queue_max_depth", "up_ms", "t_rl_fail_open", "d_dropped_events"):
            d = dict(BASE)
            d[campo] = True
            with self.assertRaises(parse_diag.DiagError) as ctx:
                parse_diag.parse_payload(json.dumps(d))
            self.assertIn("no es entero", str(ctx.exception))

    def test_bool_en_diag_v(self):
        d = dict(BASE, diag_v=True)
        with self.assertRaises(parse_diag.DiagError) as ctx:
            parse_diag.parse_payload(json.dumps(d))
        self.assertIn("diag_v no es entero", str(ctx.exception))


class TestLimites(unittest.TestCase):
    def test_minimos_y_maximos_validos(self):
        d = dict(BASE)
        for campo, (mn, mx) in parse_diag.INT_FIELDS.items():
            d[campo] = mn
        parse_diag.parse_payload(json.dumps(d))          # no debe lanzar
        for campo, (mn, mx) in parse_diag.INT_FIELDS.items():
            d[campo] = mx
        parse_diag.parse_payload(json.dumps(d))          # no debe lanzar

    def test_por_encima_del_maximo(self):
        for campo, (_mn, mx) in parse_diag.INT_FIELDS.items():
            d = dict(BASE)
            d[campo] = mx + 1
            with self.assertRaises(parse_diag.DiagError) as ctx:
                parse_diag.parse_payload(json.dumps(d))
            self.assertIn("fuera de rango", str(ctx.exception))

    def test_negativos(self):
        for campo in ("up_ms", "queue_max_depth", "t_dropped_mtu"):
            d = dict(BASE)
            d[campo] = -1
            with self.assertRaises(parse_diag.DiagError):
                parse_diag.parse_payload(json.dumps(d))

    def test_node_id_limites(self):
        parse_diag.parse_payload(json.dumps(dict(BASE, n="A")))
        parse_diag.parse_payload(json.dumps(dict(BASE, n="A" * 64)))
        for malo in ("", "A" * 65, "ESP32 CH01", "ESP32{01}"):
            with self.assertRaises(parse_diag.DiagError):
                parse_diag.parse_payload(json.dumps(dict(BASE, n=malo)))

    def test_node_id_con_espacios_de_control(self):
        # Con re.match() el ancla '$' aceptaba un salto de linea final: debe rechazarse.
        for malo in ("BAD\n", "BAD\r", "BAD\t", "\nBAD", "BAD\n\n", "BA\nD", "BAD\r\n"):
            with self.assertRaises(parse_diag.DiagError) as ctx:
                parse_diag.parse_payload(json.dumps(dict(BASE, n=malo)))
            self.assertIn("n con caracteres no permitidos", str(ctx.exception))


class TestJsonMalformado(unittest.TestCase):
    def test_json_roto(self):
        for crudo in ('{"diag_v":1', "no-es-json", "[1,2,3]", "{}"):
            with self.assertRaises(parse_diag.DiagError):
                parse_diag.parse_payload(crudo)

    def test_carga_no_objeto(self):
        with self.assertRaises(parse_diag.DiagError) as ctx:
            parse_diag.parse_payload("[1,2,3]")
        self.assertIn("no es un objeto", str(ctx.exception))


class TestLogMixto(unittest.TestCase):
    def test_ignora_lineas_ajenas_y_numera_errores(self):
        lineas = [
            "I (123) NODO: arranque\n",
            '{"v":1,"e":12,"n":"ESP32_1_CH_01"}\n',          # alerta BLE JSON v1: se ignora
            "[WARN] Eventos descartados por cola llena\n",
            linea(BASE) + "\n",                               # valida (linea 4)
            "texto suelto\n",
            linea(texto='{"diag_v":1}') + "\n",               # invalida (linea 6)
        ]
        registros, errores = parse_diag.parse_lines(lineas)
        self.assertEqual(len(registros), 1)
        self.assertEqual(len(errores), 1)
        self.assertEqual(errores[0][0], 6)                    # numero de linea exacto

    def test_solo_lineas_que_empiezan_con_prefijo(self):
        registros, errores = parse_diag.parse_lines(["  " + linea(BASE) + "\n"])
        self.assertEqual((len(registros), len(errores)), (0, 0))


class TestParidadConSchema(unittest.TestCase):
    """El parser y docs/lab/diag-schema.json deben describir el MISMO contrato."""

    @classmethod
    def setUpClass(cls):
        with open(SCHEMA_PATH, "r", encoding="utf-8") as fh:
            cls.schema = json.load(fh)

    def test_claves_requeridas_identicas(self):
        self.assertEqual(set(self.schema["required"]), set(parse_diag.REQUIRED_KEYS))

    def test_propiedades_identicas(self):
        self.assertEqual(set(self.schema["properties"]), set(parse_diag.REQUIRED_KEYS))

    def test_additional_properties_false(self):
        self.assertIs(self.schema["additionalProperties"], False)

    def test_quince_propiedades(self):
        self.assertEqual(len(self.schema["properties"]), 15)
        self.assertEqual(len(self.schema["required"]), 15)

    def test_diag_v_constante(self):
        self.assertEqual(self.schema["properties"]["diag_v"]["const"], parse_diag.DIAG_V)

    def test_node_id_coincide(self):
        prop = self.schema["properties"]["n"]
        self.assertEqual(prop["maxLength"], parse_diag.NODE_ID_MAX_LEN)
        self.assertEqual(prop["minLength"], 1)
        self.assertEqual(prop["pattern"], parse_diag.NODE_ID_RE.pattern)

    def test_rangos_enteros_coinciden(self):
        for campo, (mn, mx) in parse_diag.INT_FIELDS.items():
            prop = self.schema["properties"][campo]
            self.assertEqual(prop["minimum"], mn, campo)
            self.assertEqual(prop["maximum"], mx, campo)
            self.assertEqual(prop["type"], "integer", campo)


class TestSalida(unittest.TestCase):
    def test_csv_determinista_y_ordenado(self):
        registros, _ = parse_lines_ok()
        a, b = io.StringIO(), io.StringIO()
        parse_diag.escribir_csv(registros, a)
        parse_diag.escribir_csv(registros, b)
        self.assertEqual(a.getvalue(), b.getvalue())
        cabecera = a.getvalue().splitlines()[0]
        self.assertEqual(cabecera, ",".join(parse_diag.FIELD_ORDER))

    def test_jsonl_determinista(self):
        registros, _ = parse_lines_ok()
        a, b = io.StringIO(), io.StringIO()
        parse_diag.escribir_jsonl(registros, a)
        parse_diag.escribir_jsonl(registros, b)
        self.assertEqual(a.getvalue(), b.getvalue())
        fila = json.loads(a.getvalue().splitlines()[0])
        self.assertEqual(set(fila), set(parse_diag.FIELD_ORDER))

    def test_salida_no_copia_contenido_crudo(self):
        marca = "MARCA_CRUDA_NO_DEBE_APARECER"
        lineas = [linea(dict(BASE, n="ESP32_1_CH_01")) + "  " + marca + "\n"]
        registros, errores = parse_diag.parse_lines(lineas)
        # La linea es invalida (JSON con basura al final) y el motivo no incluye el crudo.
        self.assertEqual(len(registros), 0)
        self.assertEqual(len(errores), 1)
        self.assertNotIn(marca, errores[0][1])

    def test_errores_no_incluyen_carga(self):
        secreto = "AA:BB:CC:DD:EE:FF"
        lineas = [linea(texto='{"diag_v":1,"n":"%s"}' % secreto) + "\n"]
        _registros, errores = parse_diag.parse_lines(lineas)
        self.assertEqual(len(errores), 1)
        self.assertNotIn(secreto, errores[0][1])


class TestCliFailClosed(unittest.TestCase):
    """Ante cualquier linea invalida no debe quedar salida parcial."""

    LOG_VALIDO = linea(BASE) + "\n"
    LOG_MIXTO = linea(BASE) + "\n" + linea(texto='{"diag_v":1}') + "\n"

    def _correr(self, contenido, argv_extra):
        with tempfile.TemporaryDirectory() as tmp:
            entrada = os.path.join(tmp, "serial.log")
            with open(entrada, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(contenido)
            salida = os.path.join(tmp, "out.csv")
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                codigo = parse_diag.main([entrada] + argv_extra + ["--output", salida])
            existe = os.path.exists(salida)
            contenido_salida = ""
            if existe:
                with open(salida, "r", encoding="utf-8") as fh:
                    contenido_salida = fh.read()
            return codigo, existe, contenido_salida, out.getvalue(), err.getvalue()

    def test_valido_crea_salida(self):
        codigo, existe, texto, _out, _err = self._correr(self.LOG_VALIDO, [])
        self.assertEqual(codigo, 0)
        self.assertTrue(existe)
        self.assertIn("ESP32_1_CH_01", texto)

    def test_invalido_no_crea_salida(self):
        codigo, existe, _texto, _out, err = self._correr(self.LOG_MIXTO, [])
        self.assertEqual(codigo, 1)
        self.assertFalse(existe, "no debe crearse el archivo de salida ante error")
        self.assertIn("fail-closed", err)

    def test_invalido_no_sobrescribe_salida_previa(self):
        with tempfile.TemporaryDirectory() as tmp:
            entrada = os.path.join(tmp, "serial.log")
            with open(entrada, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(self.LOG_MIXTO)
            salida = os.path.join(tmp, "out.csv")
            previo = "CONTENIDO_PREVIO_INTACTO\n"
            with open(salida, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(previo)
            err = io.StringIO()
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
                codigo = parse_diag.main([entrada, "--output", salida])
            with open(salida, "r", encoding="utf-8") as fh:
                self.assertEqual(fh.read(), previo)
            self.assertEqual(codigo, 1)

    def test_invalido_no_escribe_en_stdout(self):
        with tempfile.TemporaryDirectory() as tmp:
            entrada = os.path.join(tmp, "serial.log")
            with open(entrada, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(self.LOG_MIXTO)
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                codigo = parse_diag.main([entrada, "--output", "-"])
            self.assertEqual(codigo, 1)
            self.assertEqual(out.getvalue(), "", "no debe emitirse salida parcial por stdout")

    def test_jsonl_invalido_tampoco_emite(self):
        codigo, existe, _t, _o, _e = self._correr(self.LOG_MIXTO, ["--format", "jsonl"])
        self.assertEqual(codigo, 1)
        self.assertFalse(existe)


def parse_lines_ok():
    return parse_diag.parse_lines([linea(BASE) + "\n", linea(dict(BASE, n="ESP32_4_SCANN")) + "\n"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
