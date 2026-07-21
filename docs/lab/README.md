# Laboratorio — Fase 8 / F6 · reglas de evidencia y sanitización

<sub>🇪🇸 Español · [🇬🇧 English](README.en.md)</sub>

Esta carpeta contiene **solo material documental**: el protocolo de laboratorio, el
esquema del contrato diagnóstico y plantillas sintéticas. **No contiene evidencia real.**

## Qué SÍ vive en el repositorio

| Archivo | Contenido |
| --- | --- |
| [`F6-protocolo.md`](F6-protocolo.md) | Protocolo de laboratorio (matriz de pruebas, campañas, criterios de aceptación) |
| [`diag-schema.json`](diag-schema.json) | Contrato formal de la línea `[DIAG]` (15 claves, tipos y rangos) |
| [`run.json.example`](run.json.example) | Plantilla **sintética** de metadata de corrida, sin PII ni ubicación |
| [`results-template.md`](results-template.md) | Plantilla de resultados **agregados y sanitizados** |
| `../../tools/parse_diag.py` | Parser de líneas `[DIAG]` (solo biblioteca estándar) |

## Qué NUNCA se versiona

La evidencia cruda puede contener **MAC, BSSID, SSID, identificadores de equipos y
metadatos de ubicación**. Queda **fuera del repositorio público**, en almacenamiento
privado del proyecto:

- capturas `*.pcap` / `*.pcapng`;
- logs de consola serie (`serial.log` y equivalentes);
- alertas recibidas en la RPi (`alerts.jsonl`);
- `run.json` **real** de cada corrida;
- cualquier contenido bajo `evidence/`.

`.gitignore` bloquea `evidence/`, `*.pcap` y `*.pcapng`. Además, el job `guards` del
CI **falla** si alguno de esos archivos aparece rastreado, permitiendo únicamente las
rutas documentales aprobadas que se listan arriba. No alcanza con renombrar un archivo
a `*.example`: la excepción es por **ruta exacta**.

## Reglas de sanitización

Lo que sí puede publicarse son **resultados agregados**:

1. **Sin direcciones reales.** Las MAC/BSSID se sustituyen por etiquetas estables del
   protocolo (`AP_LAB`, `STA_LAB_1`, `ATACANTE_LAB`). Si hace falta ilustrar un formato,
   se usan MAC de documentación ficticias.
2. **Sin PII.** `run.json` no lleva nombre, correo ni identificador del operador; se usa
   un rol (`operador_1`).
3. **Sin ubicación.** Nada de direcciones, coordenadas, planos ni nombres de sede. El
   *site survey* se reporta en distancias relativas y obstáculos genéricos.
4. **Sin SSID reales.** Se referencia la red de laboratorio como `SSID_LAB`.
5. **Solo métricas.** De las líneas `[DIAG]` se publican contadores, mínimos y máximos;
   nunca el log crudo. `parse_diag.py` produce salida determinista reconstruida desde
   valores ya validados y **no copia** la línea de entrada.

## Uso del parser

```bash
# CSV determinista a stdout (ignora líneas que no empiezan con "[DIAG] ")
python3 tools/parse_diag.py serial.log

# JSONL a archivo
python3 tools/parse_diag.py serial.log --format jsonl --output diag.jsonl
```

Cualquier línea `[DIAG]` malformada se reporta con **número de línea y motivo** (nunca
con su contenido) y el proceso termina con código distinto de cero.

> **Alcance:** F6a-2 entrega protocolo, tooling y plantillas. **No incluye encender,
> reflashear ni medir hardware**; eso corresponde a F6b/F6c.
