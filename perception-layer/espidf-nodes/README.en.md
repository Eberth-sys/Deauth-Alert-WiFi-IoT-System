> 🌐 **English** · **[Español](README.md)**

# ESP32 nodes (ESP-IDF): perception layer

⬅ Part of [Deauth-Alert](../../README.en.md)

<p align="left">
  <img alt="ESP32" src="https://img.shields.io/badge/ESP32-WROOM--32U-E7352C?logo=espressif&logoColor=white">
  <img alt="ESP-IDF" src="https://img.shields.io/badge/ESP--IDF-v5.0%2B-E7352C?logo=espressif&logoColor=white">
  <img alt="BLE" src="https://img.shields.io/badge/Bluetooth-secure%20BLE-0082FC?logo=bluetooth&logoColor=white">
  <img alt="License" src="https://img.shields.io/badge/license-Apache%202.0-blue">
</p>

Technical manual for the ESP32 nodes' ESP-IDF firmware: the same function as the Arduino variant (deauthentication detection and BLE alerting), built on Espressif's official framework.

## Table of contents

- [Overview](#overview)
- [Key features](#key-features)
- [Project structure](#project-structure)
- [Node architecture](#node-architecture)
- [Node model: ESP32-WROOM-32U](#node-model-esp32-wroom-32u)
- [BLE security parameters](#ble-security-parameters)
- [Partition file](#partition-file)
- [System configuration (sdkconfig.defaults)](#system-configuration-sdkconfigdefaults)
- [Development environment and execution](#development-environment-and-execution)
- [BLE alert to the central node](#ble-alert-to-the-central-node)
- [Additional notes](#additional-notes)
- [Validation status](#validation-status)
- [Author](#author)
- [License](#license)

## Overview

This folder contains the ESP-IDF variant of the Deauth-Alert system's perception-layer firmware. The nodes, based on ESP32-WROOM-32U microcontrollers, detect deauthentication attacks on 2.4 GHz Wi-Fi networks and send alerts over Bluetooth Low Energy (BLE) with security configured at the firmware level.

For the full system context (architecture, other layers, academic evidence), see the [main README](../../README.en.md).

## Key features

- Wi-Fi packet capture using promiscuous mode.
- Identification of deauthentication frames targeting a specific BSSID.
- Generation of alert messages with metadata: source, destination, BSSID, and channel.
- Alert transmission over BLE using a custom service and secure characteristics.
- Advanced BLE security configuration (Secure Connections and MITM protection).
- An additional node with dynamic multi-channel scanning capability.

## Project structure

```text
perception-layer/espidf-nodes/
├── config/
│   ├── config_template.h
│   └── config.h                        # excluded by .gitignore
├── ESP32_01_Deauth_Detector_CH_01/
│   ├── main/
│   │   ├── CMakeLists.txt
│   │   └── main.c
│   ├── CMakeLists.txt
│   └── sdkconfig.defaults
├── ESP32_02_Deauth_Detector_CH_06/
├── ESP32_03_Deauth_Detector_CH_11/
├── ESP32_04_Deauth_Detector_SCAN/
├── partitions.csv
└── README.md
```

## Node architecture

| Node | Channel monitored | Function | BLE name |
| --- | --- | --- | --- |
| `ESP32_01_Deauth_Detector_CH_01` | Channel 1 | Fixed monitoring | `ESP32_01_Deauth_Detector_CH_01` |
| `ESP32_02_Deauth_Detector_CH_06` | Channel 6 | Fixed monitoring | `ESP32_02_Deauth_Detector_CH_06` |
| `ESP32_03_Deauth_Detector_CH_11` | Channel 11 | Fixed monitoring | `ESP32_03_Deauth_Detector_CH_11` |
| `ESP32_04_Deauth_Detector_SCAN` | Channels 2-5, 7-14 | Rotating multi-channel scan | `ESP32_Channel_Scanner` |

All nodes share a common configuration file containing the security parameters and the UUIDs required for BLE operation.

## Node model: ESP32-WROOM-32U

| Feature | Detail |
| --- | --- |
| Processor | Dual-core Xtensa 32-bit LX6 at 240 MHz. |
| Memory | 520 KB of internal SRAM and 4 MB of SPI flash. |
| Wi-Fi | 802.11 b/g/n at 2.4 GHz, with promiscuous mode support. |
| Bluetooth | BLE 4.2 and classic Bluetooth. The firmware requests BLE Secure Connections and MITM protection (`ESP_LE_AUTH_REQ_SC_MITM`). |
| U.FL connector | Supports higher-gain external antennas. |
| Power | 2.2 V to 3.6 V range. |
| Dimensions | 18 × 25.5 × 3.1 mm. |

> The firmware requests BLE Secure Connections and MITM protection via `ESP_LE_AUTH_REQ_SC_MITM`. Whether encryption and authentication are actually enforced depends on the pairing process and the BLE client. This behavior requires specific validation in the laboratory.

## BLE security parameters

### BLE configuration file: `config.h`

1. Go to the project's `config/` folder.
2. Copy `config_template.h` and rename it to `config.h`.
3. Fill in the actual values:

```c
#define TARGET_BSSID "YOUR_TARGET_BSSID"                  // MAC address of the access point to monitor
#define SERVICE_UUID "YOUR_SERVICE_UUID"                  // BLE service UUID
#define CHARACTERISTIC_UUID "YOUR_CHARACTERISTIC_UUID"    // BLE characteristic UUID
```

This file is mandatory for every node: without a present and complete `config.h`, the firmware will not compile. `config.h` is excluded by `.gitignore`; only `config_template.h` is version-controlled.

## Partition file

`partitions.csv` defines how the ESP32's flash memory is organized:

| Name | Type | Subtype | Offset | Size | Description |
| --- | --- | --- | --- | --- | --- |
| `nvs` | data | nvs | 0x9000 | 24 KB | Non-volatile storage |
| `phy_init` | data | phy | 0xf000 | 4 KB | PHY hardware initialization |
| `factory` | app | factory | 0x10000 | 1536 KB | Main application |

## System configuration (sdkconfig.defaults)

`sdkconfig.defaults` sets the essential configuration (BLE, security, partition table), so there is no need to run `idf.py menuconfig` unless additional adjustments are required.

| Parameter | Value | Description |
| --- | --- | --- |
| `CONFIG_BT_ENABLED` | `y` | Enables general Bluetooth support. |
| `CONFIG_BT_BLE_ENABLED` | `y` | Enables BLE-specific support. |
| `CONFIG_BT_BLUEDROID_ENABLED` | `y` | Enables the Bluedroid stack used by the ESP32. |
| `CONFIG_BT_CONTROLLER_ENABLED` | `y` | Enables the Bluetooth controller. |
| `CONFIG_BTDM_CONTROLLER_MODE_BLE_ONLY` | `y` | Restricts the mode to BLE (no classic Bluetooth). |
| `CONFIG_BT_BLE_SECURE_CONN` | `y` | Enables Secure Connections. |
| `CONFIG_BT_BLE_SMP_ENABLE` | `y` | Enables the pairing protocol (SMP). |
| `CONFIG_BT_SMP_ENABLE` | `y` | Support for security key exchange. |
| `CONFIG_BT_BLE_MAX_ENCRYPTION_KEY_SIZE` | `16` | Maximum length of BLE encryption keys. |
| `CONFIG_PARTITION_TABLE_CUSTOM` | `y` | Enables a custom partition table. |
| `CONFIG_PARTITION_TABLE_CUSTOM_FILENAME` | `../partitions.csv` | Custom table file. |
| `CONFIG_PARTITION_TABLE_FILENAME` | `../partitions.csv` | File referenced as the active table. |

## Development environment and execution

Development uses ESP-IDF (Espressif IoT Development Framework), version v5.0 or later.

### Prerequisites

- ESP-IDF and a Python version compatible with the installed release. Using the official ESP-IDF installer is recommended.
- Git, to clone the repository.
- A USB cable to connect the ESP32.

### Commands to build and flash the firmware

```bash
# Activate the ESP-IDF environment
. $HOME/esp/esp-idf/export.sh

# Build the project
idf.py build

# Flash the firmware to the device
idf.py -p /dev/ttyUSB0 flash

# Start the serial monitor
idf.py -p /dev/ttyUSB0 monitor
```

`/dev/ttyUSB0` corresponds to the serial port on Linux. On Windows it usually appears as `COM3`, `COM4`, etc.; on macOS, as `/dev/cu.SLAB_USBtoUART`.

### Reproducible build with the official container (Docker)

Besides the local environment, each project (one per node) builds reproducibly with the **official Espressif container** and **ESP-IDF 5.1** (**compilation**-validated version), without installing the toolchain locally:

```bash
# Reproducible example (ESP-IDF 5.1). Adjust the mounted path to your operating system.
docker run --rm -v <PATH_espidf-nodes>:/project -w /project/<NODE> espressif/idf:release-v5.1 idf.py set-target esp32 build
```

> **Mounted-path syntax:** the `-v <path>:/project` argument **varies by operating system** (Windows/PowerShell, Linux, and macOS paths differ). Adapt `<PATH_espidf-nodes>` to the local path of `perception-layer/espidf-nodes`.

The build uses the `partitions.csv` in this folder; the binary (~1.09 MB) leaves **~31% free of the application partition** (not of the ESP32's entire flash memory).

## BLE alert to the central node

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

## Additional notes

- **Responsible use:** promiscuous mode must be used only on networks where authorization exists.
- **Security:** the `config.h` file is protected by `.gitignore` to prevent the exposure of sensitive information.
- **Wi-Fi compatibility:** this system is designed for 2.4 GHz Wi-Fi networks.

## Validation status

| Validation status |
| :--- |
| **Build validation:** compiles reproducibly with ESP-IDF 5.1 (official container). This ESP-IDF variant is an **academic adaptation** and has **no** physical hardware validation; the path historically validated with hardware was the **Arduino IDE** firmware (same function; see the Arduino variant's README). |

## Author

**Esp. Ing. Eberth Gabriel Alarcón González.** Full profile, background, and academic evidence in the [main README](../../README.en.md#about-the-author).

## License

Original code and documentation under the Apache 2.0 license. See [LICENSE](../../LICENSE) and [NOTICE](../../NOTICE) at the root of the repository.
