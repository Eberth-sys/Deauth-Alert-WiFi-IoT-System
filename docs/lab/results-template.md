# Resultados F6 — campaña `<A|B>` (plantilla)

<sub>🇪🇸 Español · [🇬🇧 English](results-template.en.md)</sub>

> Plantilla de resultados **agregados y sanitizados**. Copiar, completar y publicar.
> **Prohibido** pegar aquí logs crudos, PCAP, MAC/BSSID/SSID reales, PII o ubicaciones
> (ver [README](README.md)). Los valores se obtienen con `tools/parse_diag.py`.

## 1. Identificación de la corrida

| Campo | Valor |
| --- | --- |
| Campaña | `<A = Arduino \| B = ESP-IDF>` |
| Commit del firmware | `<sha corto>` |
| Build diagnóstico | `DEAUTH_DIAG=<0\|1>` |
| Cadena y versiones | `<Arduino Core 3.2.0 \| ESP-IDF 5.1 \| PlatformIO 6.1.16>` |
| Fecha | `<AAAA-MM-DD>` |
| Operador (rol) | `operador_1` |
| Autorización | `<referencia interna>` |
| Entorno | RF controlado, equipos y redes propios |

## 2. Resumen por nodo

| Nodo | Rol | T1 | T2 | T3 | T4 | T5 | T6 | T7 | T8 | Veredicto |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `ESP32_1_CH_01` | canal 1 | | | | | | | | | |
| `ESP32_2_CH_06` | canal 6 | | | | | | | | | |
| `ESP32_3_CH_11` | canal 11 | | | | | | | | | |
| `ESP32_4_SCANN` | scanner | | | | | | | | | |

Leyenda: ✅ cumple · ⚠️ con observación · ❌ no cumple · — no aplica.

## 3. Métricas `[DIAG]` (agregadas)

| Nodo | `stack_min_free_bytes` | `queue_max_depth` | `heap_min_free_bytes` | `mtu_negotiated` |
| --- | --- | --- | --- | --- |
| `ESP32_1_CH_01` | | | | |
| `ESP32_2_CH_06` | | | | |
| `ESP32_3_CH_11` | | | | |
| `ESP32_4_SCANN` | | | | |

`queue_max_depth` es el máximo de las **muestras** posteriores a cada encolado exitoso,
no un máximo absoluto. `mtu_negotiated` se reporta **medido**; no se afirma 247 efectivo
sin evidencia.

## 4. Contadores acumulados (fin de corrida)

| Nodo | `t_dropped_events` | `t_dropped_mtu` | `t_rl_suppressed` | `t_rl_fail_open` |
| --- | --- | --- | --- | --- |
| `ESP32_1_CH_01` | | | | |
| `ESP32_2_CH_06` | | | | |
| `ESP32_3_CH_11` | | | | |
| `ESP32_4_SCANN` | | | | |

## 5. Rate-limit — criterios separados

**SUPPRESS (clave ya registrada)**

| Nodo | Duración (s) | Tramas detectadas | Alertas emitidas | Esperado `floor(dur/1s)±1` | `t_rl_suppressed` | Veredicto |
| --- | --- | --- | --- | --- | --- | --- |
| | | | | | | |

**ALLOW_FULL (clave nueva con 8 entradas activas)**

| Nodo | Claves activas | Alertas de la clave nueva | `t_rl_fail_open` | ¿Se perdió alguna alerta legítima? | Veredicto |
| --- | --- | --- | --- | --- | --- |
| | ≥9 | | | | |

## 6. Flood — build normal vs diagnóstico

La sonda de cola solo existe con `DEAUTH_DIAG=1` e introduce una perturbación pequeña;
por eso se reportan ambos valores.

| Nodo | Tasa (tramas/s) | `d_dropped_events` (DIAG=0) | `d_dropped_events` (DIAG=1) | Observación |
| --- | --- | --- | --- | --- |
| | | | | |

## 7. Soak de estabilidad

| Nodo | Duración | `heap_min_free_bytes` inicio → fin | ¿Deriva monótona? | Reinicios | Veredicto |
| --- | --- | --- | --- | --- | --- |
| | | | | | |

> El soak **no** demuestra el wrap-around de `TickType_t` (~49,7 días), ya cubierto por
> host-tests.

## 8. DT-24 — corrida separada de baja tasa

| Escenario | `SA != BSSID` | Referencia (monitor) `addr1`/`addr2`/`addr3` | Emitido `d`/`s`/`b` | ¿Coincide? |
| --- | --- | --- | --- | --- |
| | sí | | | |

Nodos de canal fijo primero; **scanner evaluado aparte** (ventanas de channel hopping).

**Conclusión DT-24:** `<mapeo estándar confirmado | divergencia documentada | no concluyente>`

## 9. Site survey

| Punto | Distancia relativa | Obstáculos | Cobertura Wi-Fi | Enlace BLE |
| --- | --- | --- | --- | --- |
| | | | | |

> Sin direcciones, coordenadas ni planos. **No publicar una “distancia máxima BLE”** sin
> mediciones que la respalden.

## 10. Deudas afectadas

| Deuda | Estado tras la corrida | Evidencia |
| --- | --- | --- |
| DT-01 / DT-08 / DT-09 | | |
| DT-19 (MTU) | | |
| DT-22 (cola/worker) | | |
| DT-24 | | |
