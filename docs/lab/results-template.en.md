# F6 results — campaign `<A|B>` (template)

<sub>[🇪🇸 Español](results-template.md) · 🇬🇧 English</sub>

> Template for **aggregated, sanitized** results. Copy, fill in and publish.
> **Never** paste raw logs, PCAPs, real MAC/BSSID/SSID, PII or locations here
> (see [README](README.en.md)). Values come from `tools/parse_diag.py`.

## 1. Run identification

| Field | Value |
| --- | --- |
| Campaign | `<A = Arduino \| B = ESP-IDF>` |
| Firmware commit | `<short sha>` |
| Diagnostic build | `DEAUTH_DIAG=<0\|1>` |
| Toolchain and versions | `<Arduino Core 3.2.0 \| ESP-IDF 5.1 \| PlatformIO 6.1.16>` |
| Date | `<YYYY-MM-DD>` |
| Operator (role) | `operator_1` |
| Authorization | `<internal reference>` |
| Environment | Controlled RF, own equipment and networks |

## 2. Per-node summary

| Node | Role | T1 | T2 | T3 | T4 | T5 | T6 | T7 | T8 | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `ESP32_1_CH_01` | channel 1 | | | | | | | | | |
| `ESP32_2_CH_06` | channel 6 | | | | | | | | | |
| `ESP32_3_CH_11` | channel 11 | | | | | | | | | |
| `ESP32_4_SCANN` | scanner | | | | | | | | | |

Legend: ✅ pass · ⚠️ pass with note · ❌ fail · — not applicable.

## 3. `[DIAG]` metrics (aggregated)

| Node | `stack_min_free_bytes` | `queue_max_depth` | `heap_min_free_bytes` | `mtu_negotiated` |
| --- | --- | --- | --- | --- |
| `ESP32_1_CH_01` | | | | |
| `ESP32_2_CH_06` | | | | |
| `ESP32_3_CH_11` | | | | |
| `ESP32_4_SCANN` | | | | |

`queue_max_depth` is the maximum of the **samples** taken after each successful enqueue,
not an absolute maximum. `mtu_negotiated` is reported as **measured**; no effective 247
is claimed without evidence.

## 4. Cumulative counters (end of run)

| Node | `t_dropped_events` | `t_dropped_mtu` | `t_rl_suppressed` | `t_rl_fail_open` |
| --- | --- | --- | --- | --- |
| `ESP32_1_CH_01` | | | | |
| `ESP32_2_CH_06` | | | | |
| `ESP32_3_CH_11` | | | | |
| `ESP32_4_SCANN` | | | | |

## 5. Rate-limit — separate criteria

**SUPPRESS (already-registered key)**

| Node | Duration (s) | Frames detected | Alerts emitted | Expected `floor(dur/1s)±1` | `t_rl_suppressed` | Verdict |
| --- | --- | --- | --- | --- | --- | --- |
| | | | | | | |

**ALLOW_FULL (new key while 8 entries are active)**

| Node | Active keys | Alerts from the new key | `t_rl_fail_open` | Any legitimate alert lost? | Verdict |
| --- | --- | --- | --- | --- | --- |
| | ≥9 | | | | |

## 6. Flood — normal vs diagnostic build

The queue probe exists only with `DEAUTH_DIAG=1` and introduces a small perturbation;
both figures are therefore reported.

| Node | Rate (frames/s) | `d_dropped_events` (DIAG=0) | `d_dropped_events` (DIAG=1) | Note |
| --- | --- | --- | --- | --- |
| | | | | |

## 7. Stability soak

| Node | Duration | `heap_min_free_bytes` start → end | Monotonic drift? | Resets | Verdict |
| --- | --- | --- | --- | --- | --- |
| | | | | | |

> The soak does **not** demonstrate the `TickType_t` wrap-around (~49.7 days), already
> covered by host tests.

## 8. DT-24 — separate low-rate run

| Scenario | `SA != BSSID` | Reference (monitor) `addr1`/`addr2`/`addr3` | Emitted `d`/`s`/`b` | Match? |
| --- | --- | --- | --- | --- |
| | yes | | | |

Fixed-channel nodes first; **scanner evaluated separately** (channel-hopping windows).

**DT-24 conclusion:** `<standard mapping confirmed | divergence documented | inconclusive>`

## 9. Site survey

| Point | Relative distance | Obstacles | Wi-Fi coverage | BLE link |
| --- | --- | --- | --- | --- |
| | | | | |

> No addresses, coordinates or floor plans. **Do not publish a “maximum BLE distance”**
> without measurements backing it.

## 10. Affected debts

| Debt | Status after the run | Evidence |
| --- | --- | --- |
| DT-01 / DT-08 / DT-09 | | |
| DT-19 (MTU) | | |
| DT-22 (queue/worker) | | |
| DT-24 | | |
