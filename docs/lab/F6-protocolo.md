# Fase 8 / F6 — Protocolo de laboratorio

<sub>🇪🇸 Español · [🇬🇧 English](F6-protocolo.en.md)</sub>

> **Fase 8 / F6**, no confundir con la Fase 6 global de seguridad (cerrada).
> Este documento define **cómo se mide**; no ejecuta ni autoriza por sí mismo ninguna prueba.

## 0. Condiciones previas (obligatorias)

- **Entorno RF controlado** y **únicamente equipos y redes propios o expresamente
  autorizados**. Cada corrida registra la referencia de autorización en `run.json`.
- El generador de tramas de gestión (deauth/disassoc) actúa **solo contra el AP y el
  cliente de laboratorio propios**. Este documento **no incluye comandos ofensivos ni
  herramientas de ataque**: describe qué estímulo debe existir y qué se mide.
- Ninguna prueba se ejecuta sobre redes de terceros ni en espacios compartidos sin control.

## 1. Topología real

| Elemento | Cantidad | Rol |
| --- | --- | --- |
| ESP32 físicos | **4** | 3 con canal fijo (**1**, **6**, **11**) + **1 scanner** |
| Targets / variantes lógicas | **8** | 4 roles × 2 cadenas (Arduino y ESP-IDF). En gobernanza se nombran «8 variantes / 8 builds» |
| Raspberry Pi | 1 | Receptor BLE (`ble_manager.py`, parser dual) |
| Host de captura | 1 | Adaptador en **modo monitor** (referencia independiente para DT-24) |

**No existen 8 nodos físicos.** Los 8 targets son **4 roles × 2 cadenas** (Arduino y
ESP-IDF) que se ejecutan sobre los **mismos 4 equipos**.

## 2. Dos campañas sobre los mismos 4 equipos

| Campaña | Firmware | Nota |
| --- | --- | --- |
| **A** | 4 targets **Arduino** | Batería completa |
| **B** | 4 targets **ESP-IDF** | **Reflasheo** de los mismos 4 equipos; batería idéntica a A |

Los resultados se reportan por campaña para poder comparar cadena contra cadena.

## 3. Instrumentación

Las campañas se ejecutan con el **build diagnóstico** (`DEAUTH_DIAG=1`), que emite una
línea `[DIAG]` por consola serie cada **5 s** aunque no haya eventos. Contrato en
[`diag-schema.json`](diag-schema.json); extracción con `tools/parse_diag.py`.

- La línea `[DIAG]` sale **solo por serie**, nunca por BLE: el contrato BLE sigue siendo
  DEC-0003 JSON v1.
- Con `DEAUTH_DIAG=0` el firmware es **idéntico al de producción** (verificado en CI:
  0 símbolos y 0 marcador diagnóstico, secciones iguales a la base).
- **Perturbación declarada:** con `DEAUTH_DIAG=1` la sonda de cola añade una llamada y
  una sección crítica dedicada en el callback promiscuo. Por eso el flood se ejecuta
  **dos veces sobre el mismo target**: una compilación con `DEAUTH_DIAG=0` y otra con
  `DEAUTH_DIAG=1`, reportando ambos valores de `dropped_events`.
- **Precisión sobre `DEAUTH_DIAG` (conteo de artefactos):** `DEAUTH_DIAG=0` y
  `DEAUTH_DIAG=1` son **dos configuraciones de compilación de cada target** y **producen
  binarios distintos** (cambian flash, RAM y comportamiento observable). **No añaden
  roles ni dispositivos.** Se mantienen **4 ESP32 físicos** y **8 targets / variantes
  lógicas** (4 roles × 2 cadenas). Si la comparación `DIAG=0/1` se ejecuta sobre **toda
  la matriz**, se materializan **16 artefactos / configuraciones de prueba**, pero los
  targets lógicos siguen siendo **8** y los dispositivos físicos, **4**.
- `queue_max_depth` es el **máximo de las muestras** tomadas tras cada encolado exitoso,
  no un máximo absoluto: el worker puede consumir entre ambas operaciones.

## 4. Matriz de pruebas (por nodo y por campaña)

| # | Prueba | Estímulo | Qué se observa |
| --- | --- | --- | --- |
| T1 | Baseline en reposo | Sin estímulo | `[DIAG]` estable; contadores en 0; `heap_min_free_bytes` |
| T2 | Deauth nominal | 1 objetivo, baja tasa | Alerta JSON v1 en la RPi; `e:12` |
| T3 | Disassoc `0x0A` | 1 objetivo, baja tasa | Alerta con `e:10` |
| T4 | Rate-limit SUPPRESS | 1 clave `(dst,subtype)` sostenida | Ver §5 |
| T5 | Rate-limit ALLOW_FULL | **≥9** claves distintas activas | Ver §5 |
| T6 | Flood controlado | Escalones de tasa crecientes | `d_dropped_events`, `queue_max_depth`, `stack_min_free_bytes` |
| T7 | Soak de estabilidad | Carga moderada prolongada | Deriva de `heap_min_free_bytes`; sin reinicios |
| T8 | BLE real | Conexión/reconexión de la RPi | `mtu_negotiated` real; `d_dropped_mtu` |
| T9 | Site survey | Recorrido con distancias relativas | Cobertura Wi-Fi y alcance BLE |
| T10 | DT-24 | Corrida separada (§6) | Semántica `s`/`d`/`b` |

**El soak (T7) mide estabilidad prolongada.** No se usa para el *wrap-around* de
`TickType_t` (~49,7 días con tick de 1 ms), que **ya está cubierto por host-tests** y
**no** debe exigirse en laboratorio.

## 5. Criterios de aceptación del rate-limit (separados)

Se validan **por separado**; no se afirma un límite incondicional.

**SUPPRESS — clave YA REGISTRADA en la tabla**
- Bajo ataque sostenido sobre una misma clave `(dst, subtype)`: alertas emitidas
  ≈ `floor(duración_s / 1 s)` ± 1.
- `d_rl_suppressed` ≈ tramas detectadas − alertas emitidas.
- Una supresión **no renueva** la ventana (no se silencia indefinidamente).

**ALLOW_FULL — clave NUEVA con las 8 entradas activas**
- Con **≥9** claves distintas activas dentro de la misma ventana, una clave nueva
  **se permite** (fail-open) y **puede superar 1 alerta/ventana por diseño**.
- `d_rl_fail_open` > 0 y ninguna alerta legítima se pierde.

**Otros criterios**
- `d_dropped_mtu` = 0 una vez que el MTU negociado alcanza para el payload; si el MTU
  queda en 23, debe contarse y **no** enviarse nada truncado.
- **No se afirma “MTU 247 efectivo”** hasta medirlo: se reporta `mtu_negotiated` real.
- `stack_min_free_bytes` no debe acercarse a 0 bajo flood; se reporta el margen.
- `queue_max_depth` < `DEAUTH_QUEUE_DEPTH` (16) salvo saturación, que debe documentarse
  junto con la tasa de flood que la produce.

## 6. DT-24 — corrida separada de baja tasa

DT-24 (semántica `addr2`/`addr3` → `s`/`d`/`b`) **no se valida durante el flood**: sin
número de secuencia ni marca de tiempo del ESP32 no hay correlación trama a trama fiable.

1. Corrida **independiente y de baja tasa**, con tráfico **discriminante `SA != BSSID`**
   (si coinciden, la ambigüedad queda oculta y la prueba **no concluye**).
2. Adaptador en **modo monitor fijado al canal** del nodo bajo prueba, capturando como
   **ground truth independiente**; relojes sincronizados.
3. MAC **sintéticas o de laboratorio**, nunca de terceros.
4. Correlación **por escenario, subtipo, direcciones y ventana temporal** — no se promete
   correspondencia trama a trama.
5. **Primero los 3 nodos de canal fijo.** El scanner se evalúa **aparte**, porque sus
   ventanas de *channel hopping* hacen que pueda no estar en el canal en el instante del
   estímulo.

Salida: tabla de correspondencia que confirma el mapeo estándar o documenta la
divergencia. **DT-24 no se cierra sin este contraste.**

## 7. Evidencia

Estructura por corrida (**fuera del repositorio**, en almacenamiento privado):

```
evidence/<campaña>/<node_id>/
    serial.log        # crudo (NO se versiona)
    diag.jsonl        # salida de parse_diag.py
    alerts.jsonl      # alertas recibidas en la RPi (NO se versiona)
    capture.pcap      # solo T10 / DT-24 (NO se versiona)
    run.json          # metadata real (NO se versiona)
```

`run.json` sigue la plantilla [`run.json.example`](run.json.example): **sin PII y sin
ubicación**. Los resultados publicables se vuelcan en
[`results-template.md`](results-template.md), **agregados y sanitizados** según las
reglas del [README](README.md).
