> 🌐 **English** · **[Español](README.md)**

# Processing layer

⬅ Part of [Deauth-Alert](../README.en.md)

<p align="left">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white">
  <img alt="Raspberry Pi" src="https://img.shields.io/badge/Raspberry%20Pi-OS-A22846?logo=raspberrypi&logoColor=white">
  <img alt="BLE" src="https://img.shields.io/badge/Bluetooth-BLE-0082FC?logo=bluetooth&logoColor=white">
  <img alt="License" src="https://img.shields.io/badge/license-Apache%202.0-blue">
</p>

Technical manual for the processing layer: it receives BLE alerts from the ESP32 nodes, persists them to PostgreSQL, and publishes them to AWS IoT and Telegram. It runs on a Raspberry Pi, outside the Dockerized web stack.

## Table of contents

- [Overview](#overview)
- [ESP32 nodes and their role in the network](#esp32-nodes-and-their-role-in-the-network)
- [Technologies used](#technologies-used)
- [Installation on the Raspberry Pi](#installation-on-the-raspberry-pi)
- [Detecting the ESP32 nodes over Bluetooth](#detecting-the-esp32-nodes-over-bluetooth)
- [Running the project](#running-the-project)
- [ESP32 node simulator (no hardware)](#esp32-node-simulator-no-hardware)
- [Validation status](#validation-status)
- [Author](#author)
- [License](#license)

## Overview

This layer runs on a Raspberry Pi with Debian 12 (Bookworm) and acts as the system's central processing unit. The ESP32 nodes monitor Wi-Fi traffic on their respective channels and, upon detecting a deauthentication attack, send an alert over Bluetooth Low Energy (BLE). This layer receives those alerts, processes them, stores them in PostgreSQL, and publishes them to AWS IoT and Telegram.

For the full system context (architecture, other layers, academic evidence), see the [main README](../README.en.md).

## ESP32 nodes and their role in the network

The system comprises four ESP32 nodes, each advertised over BLE under a fixed name. The processing layer identifies each node by that name, defined in `config/devices.yaml`:

| Node BLE name | Role |
| --- | --- |
| `ESP32_1_CH_01` | Monitors channel 1. |
| `ESP32_2_CH_06` | Monitors channel 6. |
| `ESP32_3_CH_11` | Monitors channel 11. |
| `ESP32_4_SCANN` | Scans channels 2-5, 7-10, and 12-13. |

Each ESP32 captures the Wi-Fi packets on its channel and, if it detects a potential deauthentication attack, sends an alert to the Raspberry Pi over BLE.

## Technologies used

### Hardware

| Component | Description |
| --- | --- |
| Raspberry Pi 5 (8 GB RAM) | Central processing unit; runs this layer on Debian 12 (Bookworm). |
| ESP32-WROOM-32U | Module with 2.4 GHz Wi-Fi and BLE connectivity, plus an external antenna. |

### Software

| Technology | Version | Description |
| --- | --- | --- |
| Python | 3.11 | Included by default in Debian 12 (Bookworm); the version used during development. |
| BlueZ | System stack | The Linux Bluetooth stack that manages the BLE connections. |
| Bleak | 0.22.3 | Python library for communicating with BLE devices. |
| PyYAML | 6.0.3 | Reads `devices.yaml`. |
| asyncio | Included in Python 3 | Asynchronous tasks for real-time processing. |

> The direct Python dependencies are version-pinned in `requirements.txt` for reproducibility. Bleak is kept on the 0.x series and paho-mqtt on the 1.x series for compatibility with the API the code relies on.

## Installation on the Raspberry Pi

### 1. Install the operating system

1. Download Raspberry Pi OS (Debian 12, Bookworm) from [raspberrypi.com/software](https://www.raspberrypi.com/software/).
2. Flash the image onto an SD card with Raspberry Pi Imager.
3. Configure SSH and Wi-Fi for remote access (optional).

### 2. Connect to the Raspberry Pi over SSH

```bash
ssh pi@<IP_DE_LA_RASPBERRY_PI>
```

### 3. Update the system and install dependencies

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install git python3 python3-pip python3-venv bluetooth bluez -y
```

| Package | Purpose |
| --- | --- |
| `git` | Clone the repository. |
| `python3`, `python3-pip`, `python3-venv` | Run the project in a virtual environment. |
| `bluetooth`, `bluez` | Manage the BLE connections on the Raspberry Pi. |

### 4. Clone the repository

```bash
cd ~
git clone https://github.com/Eberth-sys/Deauth-Alert-WiFi-IoT-System.git
cd Deauth-Alert-WiFi-IoT-System/processing-layer
```

> The repository already contains this layer inside the `processing-layer/` folder; there's no need to switch branches.

### 5. Create and activate a virtual environment

```bash
python3 -m venv ble
source ble/bin/activate
```

The terminal prompt should show the active environment, for example `(ble) pi@raspberrypi:~/Deauth-Alert-WiFi-IoT-System/processing-layer $`.

### 6. Install the dependencies

```bash
pip install -r requirements.txt
```

## Detecting the ESP32 nodes over Bluetooth

To verify that the ESP32 nodes advertise their presence over BLE:

```bash
bluetoothctl
scan on
```

Expected output:

```
[NEW] Device AA:BB:CC:DD:EE:FF ESP32_1_CH_01
[NEW] Device 11:22:33:44:55:66 ESP32_2_CH_06
```

If the devices show up in the list, they are ready to connect.

### Troubleshooting

If Bluetooth doesn't detect the ESP32 nodes, confirm that they are powered on and running the loaded firmware. If the problem persists:

```bash
sudo systemctl restart bluetooth
bluetoothctl
scan on
```

If you run into permission issues, add the user to the `bluetooth` group and reboot:

```bash
sudo usermod -aG bluetooth pi
sudo reboot
```

## Running the project

### 1. Configure `devices.yaml`

Copy the template and fill it in with the real MAC addresses of the ESP32 nodes and the BLE service UUIDs:

```bash
cp config/devices.yaml.example config/devices.yaml
nano config/devices.yaml
```

```yaml
# Replace the MAC addresses and UUIDs with the real values before running the system.

esp32_devices:
  - address: "AA:BB:CC:DD:EE:FF"
    name: "ESP32_1_CH_01"
  - address: "11:22:33:44:55:66"
    name: "ESP32_2_CH_06"
  - address: "22:33:44:55:66:77"
    name: "ESP32_3_CH_11"
  - address: "33:44:55:66:77:88"
    name: "ESP32_4_SCANN"

uuids:
  service_uuid: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
  characteristic_uuid: "yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy"
```

### 2. Run the main script

```bash
python main.py
```

Expected output:

```
[INFO] Buscando ESP32_1_CH_01...
[CONNECTED] Conectado a ESP32_1_CH_01
[INFO] Esperando datos de ESP32_1_CH_01...
```

## ESP32 node simulator (no hardware)

The repository includes the `tools/simulate_esp32.py` tool (at the root), which reproduces the alert writes this layer performs when it receives a BLE event: it inserts deauthentication alerts into PostgreSQL's `alerts` table, using the same columns as the `guardar_alerta` function, and marks all four nodes as connected. It is a data simulation (a _mock_) meant to test the system end to end without the ESP32 nodes or the Raspberry Pi; it does not carry out a real attack, nor does it emulate the firmware or the BLE transport.

The instructions for running it are in the [main README](../README.en.md#try-it-without-hardware-esp32-node-simulator).

## Validation status

| Validation status |
| :--- |
| This layer was tested in the lab with real hardware (ESP32 nodes and a Raspberry Pi) and worked as part of the thesis prototype. The direct Python dependencies are version-pinned in `requirements.txt`. |

## Author

**Esp. Ing. Eberth Gabriel Alarcón González.** Full profile, background, and academic evidence in the [main README](../README.en.md#about-the-author).

## License

Original code and documentation under the Apache 2.0 license. See [LICENSE](../LICENSE) and [NOTICE](../NOTICE) at the root of the repository.
