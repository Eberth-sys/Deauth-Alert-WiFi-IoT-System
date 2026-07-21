# Phase 8 / F6 — Lab protocol

<sub>[🇪🇸 Español](F6-protocolo.md) · 🇬🇧 English</sub>

> **Phase 8 / F6** — not to be confused with the global Phase 6 (security, closed).
> This document defines **how measurements are taken**; it neither runs nor authorizes any test by itself.

## 0. Preconditions (mandatory)

- **Controlled RF environment** and **only equipment and networks that are our own or
  explicitly authorized**. Every run records the authorization reference in `run.json`.
- The management-frame generator (deauth/disassoc) acts **only against our own lab AP and
  client**. This document contains **no offensive commands and no attack tooling**: it
  describes which stimulus must exist and what is measured.
- No test runs against third-party networks or in uncontrolled shared spaces.

## 1. Actual topology

| Item | Count | Role |
| --- | --- | --- |
| Physical ESP32 | **4** | 3 on fixed channels (**1**, **6**, **11**) + **1 scanner** |
| Logical targets / variants | **8** | 4 roles × 2 toolchains (Arduino and ESP-IDF). Governance names them "8 variants / 8 builds" |
| Raspberry Pi | 1 | BLE receiver (`ble_manager.py`, dual parser) |
| Capture host | 1 | **Monitor-mode** adapter (independent reference for DT-24) |

**There are no 8 physical nodes.** The 8 targets are **4 roles × 2 toolchains** (Arduino
and ESP-IDF) running on the **same 4 devices**.

## 2. Two campaigns over the same 4 devices

| Campaign | Firmware | Note |
| --- | --- | --- |
| **A** | 4 **Arduino** targets | Full battery |
| **B** | 4 **ESP-IDF** targets | **Reflash** of the same 4 devices; battery identical to A |

Results are reported per campaign so the two toolchains can be compared.

## 3. Instrumentation

Campaigns run the **diagnostic build** (`DEAUTH_DIAG=1`), which emits one `[DIAG]` line
on the serial console every **5 s** even with no events. Contract in
[`diag-schema.json`](diag-schema.json); extraction with `tools/parse_diag.py`.

- The `[DIAG]` line goes **over serial only**, never over BLE: the BLE contract remains
  DEC-0003 JSON v1.
- With `DEAUTH_DIAG=0` the firmware is **identical to production** (verified in CI:
  0 symbols and 0 diagnostic marker, sections equal to the baseline).
- **Declared perturbation:** with `DEAUTH_DIAG=1` the queue probe adds one call and a
  dedicated critical section inside the promiscuous callback. The flood test is therefore
  run **twice on the same target**: once compiled with `DEAUTH_DIAG=0` and once with
  `DEAUTH_DIAG=1`, reporting both `dropped_events` figures.
- **Note on `DEAUTH_DIAG` (artifact count):** `DEAUTH_DIAG=0` and `DEAUTH_DIAG=1` are
  **two build configurations of each target** and **produce different binaries** (flash,
  RAM and observable behaviour all change). **They add neither roles nor devices.** There
  are still **4 physical ESP32** and **8 logical targets / variants** (4 roles ×
  2 toolchains). If the `DIAG=0/1` comparison is run across **the whole matrix**,
  **16 artifacts / test configurations** materialize, yet the logical targets remain **8**
  and the physical devices **4**.
- `queue_max_depth` is the **maximum of the samples** taken right after each successful
  enqueue, not an absolute maximum: the worker may consume in between.

## 4. Test matrix (per node, per campaign)

| # | Test | Stimulus | Observed |
| --- | --- | --- | --- |
| T1 | Idle baseline | None | Stable `[DIAG]`; counters at 0; `heap_min_free_bytes` |
| T2 | Nominal deauth | 1 target, low rate | JSON v1 alert on the RPi; `e:12` |
| T3 | Disassoc `0x0A` | 1 target, low rate | Alert with `e:10` |
| T4 | Rate-limit SUPPRESS | 1 sustained `(dst,subtype)` key | See §5 |
| T5 | Rate-limit ALLOW_FULL | **≥9** distinct active keys | See §5 |
| T6 | Controlled flood | Increasing rate steps | `d_dropped_events`, `queue_max_depth`, `stack_min_free_bytes` |
| T7 | Stability soak | Prolonged moderate load | `heap_min_free_bytes` drift; no resets |
| T8 | Real BLE | RPi connect/reconnect | Real `mtu_negotiated`; `d_dropped_mtu` |
| T9 | Site survey | Walk-through, relative distances | Wi-Fi coverage and BLE range |
| T10 | DT-24 | Separate run (§6) | `s`/`d`/`b` semantics |

**The soak (T7) measures prolonged stability.** It is not used for the `TickType_t`
wrap-around (~49.7 days at a 1 ms tick), which is **already covered by host tests** and
must **not** be demanded in the lab.

## 5. Rate-limit acceptance criteria (separate)

Validated **separately**; no unconditional limit is claimed.

**SUPPRESS — key ALREADY REGISTERED in the table**
- Under sustained attack on the same `(dst, subtype)` key: emitted alerts
  ≈ `floor(duration_s / 1 s)` ± 1.
- `d_rl_suppressed` ≈ detected frames − emitted alerts.
- A suppression **does not renew** the window (it never goes silent indefinitely).

**ALLOW_FULL — NEW key while the 8 entries are active**
- With **≥9** distinct keys active inside the same window, a new key **is allowed**
  (fail-open) and **may exceed 1 alert per window by design**.
- `d_rl_fail_open` > 0 and no legitimate alert is lost.

**Other criteria**
- `d_dropped_mtu` = 0 once the negotiated MTU fits the payload; if the MTU stays at 23 it
  must be counted and **nothing truncated** may be sent.
- **No “effective MTU 247” is claimed** until measured: the real `mtu_negotiated` is reported.
- `stack_min_free_bytes` must not approach 0 under flood; the margin is reported.
- `queue_max_depth` < `DEAUTH_QUEUE_DEPTH` (16) unless saturated, which must be documented
  together with the flood rate that causes it.

## 6. DT-24 — separate low-rate run

DT-24 (`addr2`/`addr3` → `s`/`d`/`b` semantics) is **not validated during the flood**:
without an ESP32 sequence number or timestamp there is no reliable frame-by-frame
correlation.

1. **Independent, low-rate** run with **discriminating `SA != BSSID`** traffic (if they
   coincide the ambiguity stays hidden and the test is **inconclusive**).
2. Monitor-mode adapter **locked to the channel** of the node under test, capturing as an
   **independent ground truth**; clocks synchronized.
3. **Synthetic or lab** MAC addresses only, never third-party ones.
4. Correlation **by scenario, subtype, addresses and time window** — no frame-by-frame
   correspondence is promised.
5. **The 3 fixed-channel nodes first.** The scanner is evaluated **separately**, because
   its channel-hopping windows mean it may not be on the channel at the moment of the
   stimulus.

Output: a correspondence table confirming the standard mapping or documenting the
divergence. **DT-24 is not closed without this comparison.**

## 7. Evidence

Per-run layout (**outside the repository**, in private storage):

```
evidence/<campaign>/<node_id>/
    serial.log        # raw (NOT committed)
    diag.jsonl        # parse_diag.py output
    alerts.jsonl      # alerts received on the RPi (NOT committed)
    capture.pcap      # T10 / DT-24 only (NOT committed)
    run.json          # real metadata (NOT committed)
```

`run.json` follows the [`run.json.example`](run.json.example) template: **no PII and no
location**. Publishable results go into [`results-template.en.md`](results-template.en.md),
**aggregated and sanitized** per the [README](README.en.md) rules.
