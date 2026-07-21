# Lab — Phase 8 / F6 · evidence and sanitization rules

<sub>[🇪🇸 Español](README.md) · 🇬🇧 English</sub>

This folder holds **documentation only**: the lab protocol, the diagnostic contract
schema and synthetic templates. **It contains no real evidence.**

## What DOES live in the repository

| File | Content |
| --- | --- |
| [`F6-protocolo.en.md`](F6-protocolo.en.md) | Lab protocol (test matrix, campaigns, acceptance criteria) |
| [`diag-schema.json`](diag-schema.json) | Formal contract of the `[DIAG]` line (15 keys, types and ranges) |
| [`run.json.example`](run.json.example) | **Synthetic** run-metadata template, no PII and no location |
| [`results-template.en.md`](results-template.en.md) | Template for **aggregated, sanitized** results |
| `../../tools/parse_diag.py` | `[DIAG]` line parser (standard library only) |

## What is NEVER committed

Raw evidence may contain **MAC, BSSID, SSID, device identifiers and location
metadata**. It stays **outside the public repository**, in the project's private
storage:

- `*.pcap` / `*.pcapng` captures;
- serial console logs (`serial.log` and equivalents);
- alerts received on the RPi (`alerts.jsonl`);
- the **real** `run.json` of each run;
- anything under `evidence/`.

`.gitignore` blocks `evidence/`, `*.pcap` and `*.pcapng`. In addition, the CI `guards`
job **fails** if any of those files becomes tracked, allowing only the approved
documentation paths listed above. Renaming a file to `*.example` is not enough: the
exception is by **exact path**.

## Sanitization rules

Only **aggregated results** may be published:

1. **No real addresses.** MAC/BSSID are replaced with stable protocol labels
   (`AP_LAB`, `STA_LAB_1`, `ATTACKER_LAB`). Where a format must be illustrated, use
   fictitious documentation MAC addresses.
2. **No PII.** `run.json` carries no operator name, e-mail or identifier; use a role
   (`operator_1`).
3. **No location.** No addresses, coordinates, floor plans or site names. The site
   survey is reported as relative distances and generic obstacles.
4. **No real SSIDs.** Refer to the lab network as `SSID_LAB`.
5. **Metrics only.** From `[DIAG]` lines, publish counters, minima and maxima — never
   the raw log. `parse_diag.py` emits deterministic output rebuilt from already
   validated values and **never copies** the input line.

## Using the parser

```bash
# Deterministic CSV on stdout (ignores lines not starting with "[DIAG] ")
python3 tools/parse_diag.py serial.log

# JSONL to a file
python3 tools/parse_diag.py serial.log --format jsonl --output diag.jsonl
```

Any malformed `[DIAG]` line is reported with its **line number and reason** (never its
content) and the process exits with a non-zero status.

> **Scope:** F6a-2 delivers protocol, tooling and templates. It does **not** include
> powering, reflashing or measuring hardware; that belongs to F6b/F6c.
