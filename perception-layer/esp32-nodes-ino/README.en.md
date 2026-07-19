> 🌐 **English** · **[Español](README.md)**

# ESP32 Nodes (Arduino): Perception Layer

⬅ Part of [Deauth-Alert](../../README.en.md)

<p align="left">
  <img alt="ESP32" src="https://img.shields.io/badge/ESP32-WROOM--32U-E7352C?logo=espressif&logoColor=white">
  <img alt="Arduino" src="https://img.shields.io/badge/Arduino-C%2B%2B-00979D?logo=arduino&logoColor=white">
  <img alt="BLE" src="https://img.shields.io/badge/Bluetooth-Secure%20BLE-0082FC?logo=bluetooth&logoColor=white">
  <img alt="License" src="https://img.shields.io/badge/license-Apache%202.0-blue">
</p>

Technical manual for the Arduino firmware of the ESP32 nodes: it captures Wi-Fi frames in promiscuous mode, detects deauthentication (deauth) attacks, and sends the alert over BLE to the processing layer.

## Table of Contents

- [Perception Layer (Arduino IDE)](#perception-layer-arduino-ide)
- [Project Structure](#project-structure)
- [Detailed Node Operation](#detailed-node-operation)
- [Node Model: ESP32-WROOM-32U](#node-model-esp32-wroom-32u)
- [Setup and Usage Guide](#setup-and-usage-guide)
- [Recommended Configuration Parameters](#recommended-configuration-parameters)
- [BLE Alert to the Central Node](#ble-alert-to-the-central-node)
- [Additional Notes](#additional-notes)
- [Validation Status](#validation-status)
- [Author](#author)
- [License](#license)

## Perception Layer (Arduino IDE)

This directory contains the Arduino firmware for the ESP32 nodes of the thesis project "Sistema IoT para el Monitoreo y Detección de Ataques de Desautenticación en Redes Wi-Fi". Each node scans 2.4 GHz Wi-Fi networks for deauthentication attacks, captures the packets in promiscuous mode, and sends alerts to the central node (the Raspberry Pi in the processing layer) over BLE.

For the full system context (architecture, other layers, academic evidence), see the [main README](../../README.en.md).

## Project Structure

Each node lives in its own folder:

```text
perception-layer/esp32-nodes-ino/
├── ESP32_01_Deauth_Detector_CH_01/
│   ├── config_template.h               # Configuration template
│   ├── config.h                        # excluded by .gitignore
│   └── main.ino                        # Channel 1 scanning
├── ESP32_02_Deauth_Detector_CH_06/     # Channel 6 scanning
├── ESP32_03_Deauth_Detector_CH_11/     # Channel 11 scanning
├── ESP32_04_Deauth_Detector_SCANN/     # Dynamic scanning across multiple channels
└── README.md
```

Inside each folder:

- `config_template.h`: a template with placeholders.
- `config.h`: the real definitions; ignored by `.gitignore`.
- `main.ino`: the source code with the detection and notification logic.

## Detailed Node Operation

### Channel Scanning Modes

- `ESP32_01_Deauth_Detector_CH_01`: monitors channel 1.
- `ESP32_02_Deauth_Detector_CH_06`: monitors channel 6.
- `ESP32_03_Deauth_Detector_CH_11`: monitors channel 11.
- `ESP32_04_Deauth_Detector_SCANN`: scans channels 2-5, 7-10, and 12-13.

Each node captures Wi-Fi packets, then parses and detects deauthentication frames directed at the target BSSID. When it detects an attack, it generates an alert and sends it to the central node.

## Node Model: ESP32-WROOM-32U

| Feature | Detail |
| --- | --- |
| Processor | Dual-core Xtensa 32-bit LX6 at 240 MHz. |
| Memory | 520 KB of internal SRAM and 4 MB of SPI flash. |
| Wi-Fi | 802.11 b/g/n at 2.4 GHz, with promiscuous mode support. |
| Bluetooth | BLE 4.2 and classic Bluetooth. The firmware requests BLE Secure Connections and MITM protection (`ESP_LE_AUTH_REQ_SC_MITM`). |
| U.FL connector | Supports higher-gain external antennas. |
| Power supply | Range of 2.2 V to 3.6 V. |
| Dimensions | 18 × 25.5 × 3.1 mm. |

> The firmware requests BLE Secure Connections and MITM protection through `ESP_LE_AUTH_REQ_SC_MITM`. Whether encryption and authentication are actually enforced depends on the pairing process and the BLE client. This behavior requires specific validation in the lab.

### Initialization Process

On startup, `main.ino` runs:

1. Serial monitor (115200 baud) for local tracking.
2. Wi-Fi interface in station mode (`WIFI_STA`).
3. BLE configuration: `BLEDevice::init("ESP32_[CHANNEL]")`, a service with `SERVICE_UUID` and a *notify* characteristic (`CHARACTERISTIC_UUID`), and security configuration with `BLESecurity` (`ESP_LE_AUTH_REQ_SC_MITM`).
4. Registration of the Wi-Fi callback: `esp_wifi_set_promiscuous(true)` and `esp_wifi_set_promiscuous_rx_cb(&sniffer_callback)`.

### Deauthentication Frame Detection

In `sniffer_callback`, the node parses the received packet, checks whether it is a deauthentication frame, and compares the BSSID (`addr3`) against `TARGET_BSSID`. If they match, it extracts the source MAC (`addr2`), the destination MAC (`addr1`), and the channel (`pkt->rx_ctrl.channel`).

### Building and Sending the Alert

When it detects an attack, the node builds a string with the event data, prints it to the serial monitor, and notifies the connected BLE client through `pCharacteristic->setValue(...)` and `pCharacteristic->notify()`.

## Setup and Usage Guide

### 1. Clone the Repository

```bash
git clone https://github.com/Eberth-sys/Deauth-Alert-WiFi-IoT-System.git
cd Deauth-Alert-WiFi-IoT-System/perception-layer/esp32-nodes-ino/ESP32_01_Deauth_Detector_CH_01
```

### 2. Prepare the `config.h` File

```bash
cp config_template.h config.h
```

Edit `config.h` and replace the example values:

```cpp
#define TARGET_BSSID        "XX:XX:XX:XX:XX:XX"
#define SERVICE_UUID        "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
#define CHARACTERISTIC_UUID "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
```

Confirm that `config.h` is listed in `.gitignore` before compiling.

### 3. Upload the Firmware with the Arduino IDE

The path with **physical validation** (hardware) is the Arduino IDE. The repository **also includes a PlatformIO configuration** (see *Reproducible build with PlatformIO*), validated **by compilation only**.

1. Open `main.ino` via **File > Open** in the Arduino IDE.
2. Verify that the `#include "config.h"` line is active (the file must exist, as set up in the previous step).
3. Under **Tools > Board**, select **ESP32 Dev Module**.
4. Configure the following under **Tools**:
   - Upload Speed: 921600 baud.
   - Serial Monitor: 115200 baud.
   - Partition Scheme: Minimal SPIFFS (1.9 MB APP + 190 KB SPIFFS).
5. Connect the ESP32 over USB and identify the serial port under **Tools > Port**.
6. Hold down the **BOOT** button on the ESP32 and click **Upload**.
7. Open the Serial Monitor (**Ctrl+Shift+M**) and confirm the startup messages and the alerts:

```text
[INFO]  Modo promiscuo activo | Canal: <N>
{"v":1,"e":12,"n":"ESP32_1_CH_01","s":"01:01:01:01:01:01","d":"FF:FF:FF:FF:FF:FF","b":"01:01:01:01:01:01","c":1}
```

### Reproducible build with the Arduino CLI

Besides the IDE, the firmware builds reproducibly with the **Arduino CLI** and the **`esp32:esp32` core 3.2.0** (**compilation**-validated version). The **default partition scheme (~1.3 MB application) is not enough** for this firmware (~1.63 MB); use **Minimal SPIFFS (1.9 MB application)** or **Huge APP (3 MB application, no OTA)**.

```bash
# Validated core: esp32:esp32 3.2.0 · Arduino CLI 1.5.1
arduino-cli compile --fqbn esp32:esp32:esp32:PartitionScheme=huge_app <sketch_folder>
```

> **Build vs. physical validation:** this path (Arduino CLI + core 3.2.0) validates that the firmware **compiles**. **Physical validation on hardware** was done only via the **Arduino IDE** (see *Validation Status*).

### Reproducible build with PlatformIO

Each node is a **standalone PlatformIO project** (a minimal `platformio.ini` per folder) that inherits the shared configuration from [`pio_common.ini`](pio_common.ini) (platform, board, framework, and partition). The `main.ino` files are **not moved or modified**, so the Arduino IDE keeps working the same.

- **PINNED platform:** `pioarduino 54.03.20` -> **Arduino Core ESP32 3.2.0** (validated). Do not use `stable`/`latest`.
- **Shared Huge APP partition:** [`partitions_huge_app.csv`](partitions_huge_app.csv) (~3 MB app, no OTA, for 4 MB flash). The default partition **is not enough** (firmware ~1.65 MB).
- **Compilation-validated** with **PlatformIO Core 6.1.16** (4/4 nodes: `Flash 52.4%` of 3 MB, RAM 18.1%). This is not physical validation.

Install the pinned PlatformIO Core version and run the commands **from `perception-layer/esp32-nodes-ino/`**:

```bash
# Reproducible install (pinned version):
python -m pip install platformio==6.1.16

# Build one node (create its config.h from config_template.h first):
pio run -d ESP32_01_Deauth_Detector_CH_01

# Build all four (sequence, Bash):
for d in ESP32_0*/; do pio run -d "$d"; done
```

Equivalent PowerShell sequence:

```powershell
Get-ChildItem -Directory ESP32_0* | ForEach-Object { pio run -d $_.FullName }
```

> **Windows — long paths:** the `checkprogsize` step may fail (*"filename or extension is too long"*) if the project sits in a very long path (e.g., OneDrive). Build from a short path, enable *long paths*, or set `PLATFORMIO_CORE_DIR`/`PLATFORMIO_BUILD_DIR` to short paths (not stored in the repo).

### Shared libraries (`WifiMgmtParser`, `DeauthEvent`, `DeauthJson`)

Three **portable shared libraries** live in `perception-layer/shared/` and are consumed by all three build chains (Arduino, PlatformIO, and ESP-IDF) from a **single source**:

- **`WifiMgmtParser`** (F4b) — 802.11 header parsing (type/subtype classification and address extraction); `#include <wifi_mgmt_parser.h>`.
- **`DeauthEvent`** (F4c-1) — POD event model (20 B) + canonical BSSID parser; `#include <deauth_event.h>`.
- **`DeauthJson`** (F5-1) — v1 contract JSON serializer via `snprintf` (no heap, no JSON library); `#include <deauth_json.h>` (depends on `DeauthEvent`).

**Arduino IDE** — install the **three** libraries into the *sketchbook* (once):

- **Option A (copy the folders):** copy each folder under `perception-layer/shared/` into the sketchbook's libraries folder, resulting in:

  ```text
  <Sketchbook>/libraries/WifiMgmtParser/   (library.properties + src/)
  <Sketchbook>/libraries/DeauthEvent/      (library.properties + src/)
  <Sketchbook>/libraries/DeauthJson/       (library.properties + src/)
  ```

  `<Sketchbook>` is the folder shown under *File > Preferences > Sketchbook location* (by default `~/Arduino` on Linux/macOS or `Documents\Arduino` on Windows).

- **Option B (Add .ZIP Library):** zip each folder (`WifiMgmtParser/`, `DeauthEvent/`, `DeauthJson/`) and use *Sketch > Include Library > Add .ZIP Library…* for each one.

Restart the IDE after installing them. With all three present, `main.ino` compiles with the `#include` lines active.

The other flows need no extra install: **Arduino CLI** resolves them with `--libraries perception-layer/shared`; **PlatformIO**, with `lib_extra_dirs = ../../shared` (inherited from [`pio_common.ini`](pio_common.ini)); **ESP-IDF**, as CMake components (`EXTRA_COMPONENT_DIRS` + `REQUIRES WifiMgmtParser DeauthEvent DeauthJson`).

> **Build vs. physical validation:** the CI validates the library through **12 compilations** (4 Arduino + 4 ESP-IDF + 4 PlatformIO) and **host tests** (unit + ASAN/UBSAN + C/C++ linkage + fuzzing). It does **not** imply hardware testing; physical acceptance of the nodes remains pending in the lab.

## Recommended Configuration Parameters

| Parameter | Value |
| --- | --- |
| Board | ESP32 Dev Module |
| Upload Speed | 921600 baud |
| Serial Monitor | 115200 baud |
| Partition Scheme | Minimal SPIFFS (1.9 MB APP + 190 KB SPIFFS) |
| CPU Frequency | 240 MHz |
| Flash Mode | QIO |
| Flash Frequency | 80 MHz |
| Flash Size | 4 MB (32 Mb) |
| PSRAM | Disabled |
| Core Debug Level | None |
| Erase All Flash Before Sketch Upload | Disabled |
| Events Run On / Arduino Runs On | Core 1 |
| JTAG Adapter | Disabled |
| Zigbee Mode | Disabled |

## BLE Alert to the Central Node

Example of a generated alert (v1 JSON contract, `DeauthJson`):

```json
{"v":1,"e":12,"n":"ESP32_1_CH_01","s":"01:01:01:01:01:01","d":"FF:FF:FF:FF:FF:FF","b":"01:01:01:01:01:01","c":1}
```

```json
{"v":1,"e":10,"n":"ESP32_2_CH_06","s":"02:02:02:02:02:02","d":"AA:BB:CC:DD:EE:FF","b":"02:02:02:02:02:02","c":6}
```

- **`v`:** event-contract version (`1` in this version).
- **`e`:** 802.11 management-frame subtype — `12` = deauthentication, `10` = disassociation.
- **`n`:** canonical node identifier (`node_id`; see `devices.yaml.example`).
- **`s`:** reported source address, per the current mapping.
- **`d`:** reported destination address (`FF:FF:FF:FF:FF:FF` = broadcast, all clients).
- **`b`:** reported BSSID.
- **`c`:** Wi-Fi channel (1–14) on which the frame was detected (consistent with the `CH_xx` in the `node_id`).

The new firmware emits this v1 JSON; the Raspberry Pi keeps a **dual parser** (it accepts both the new JSON and the legacy text). The current address mapping (`s`/`d`/`b`) is preserved; its final semantic validation is pending lab work (DT-24).

*(Example MAC addresses; they do not correspond to real hardware.)*

## Additional Notes

- **Responsible use:** promiscuous mode must be used only on networks where you have authorization.
- **Security:** the `config.h` file is protected by `.gitignore` to prevent exposing sensitive information.
- **Wi-Fi compatibility:** this system is designed for 2.4 GHz Wi-Fi networks.

## Validation Status

| Validation status |
| :--- |
| This firmware was tested in the lab with real hardware (ESP32-WROOM-32U nodes) and worked as part of the thesis prototype. |

## Author

**Esp. Ing. Eberth Gabriel Alarcón González.** Full profile, background, and academic evidence in the [main README](../../README.en.md#about-the-author).

## License

Original code and documentation under the Apache 2.0 license. See [LICENSE](../../LICENSE) and [NOTICE](../../NOTICE) in the repository root.
