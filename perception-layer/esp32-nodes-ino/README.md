# Nodos ESP32 (Arduino): capa de percepción

⬅ Parte de [Deauth-Alert](../../README.md)

<p align="left">
  <img alt="ESP32" src="https://img.shields.io/badge/ESP32-WROOM--32U-E7352C?logo=espressif&logoColor=white">
  <img alt="Arduino" src="https://img.shields.io/badge/Arduino-C%2B%2B-00979D?logo=arduino&logoColor=white">
  <img alt="BLE" src="https://img.shields.io/badge/Bluetooth-BLE%20seguro-0082FC?logo=bluetooth&logoColor=white">
  <img alt="Licencia" src="https://img.shields.io/badge/licencia-pendiente-lightgrey">
</p>

Manual técnico del firmware Arduino de los nodos ESP32: captura tramas Wi-Fi en modo promiscuo, detecta ataques de desautenticación y envía la alerta por BLE a la capa de procesamiento.

## Índice

- [Capa de percepción (Arduino IDE)](#capa-de-percepción-arduino-ide)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Funcionamiento detallado de los nodos](#funcionamiento-detallado-de-los-nodos)
- [Modelo de nodo: ESP32-WROOM-32U](#modelo-de-nodo-esp32-wroom-32u)
- [Guía de configuración y uso](#guía-de-configuración-y-uso)
- [Parámetros de configuración recomendados](#parámetros-de-configuración-recomendados)
- [Alerta BLE al nodo centralizador](#alerta-ble-al-nodo-centralizador)
- [Notas adicionales](#notas-adicionales)
- [Estado de validación](#estado-de-validación)
- [Autor](#autor)
- [Licencia](#licencia)

## Capa de percepción (Arduino IDE)

Este directorio contiene el firmware Arduino de los nodos ESP32 del proyecto de tesis "Sistema IoT para el Monitoreo y Detección de Ataques de Desautenticación en Redes Wi-Fi". Cada nodo escanea redes Wi-Fi de 2,4 GHz en busca de ataques de desautenticación, captura los paquetes en modo promiscuo y envía alertas al nodo centralizador (la Raspberry Pi de la capa de procesamiento) por BLE.

Para el contexto completo del sistema (arquitectura, otras capas, evidencia académica), ver el [README principal](../../README.md).

## Estructura del proyecto

Cada nodo se aloja en una carpeta independiente:

```text
perception-layer/esp32-nodes-ino/
├── ESP32_01_Deauth_Detector_CH_01/
│   ├── config_template.h               # Plantilla para configuración
│   ├── config.h                        # excluido por .gitignore
│   └── main.ino                        # Escaneo en canal 1
├── ESP32_02_Deauth_Detector_CH_06/     # Escaneo en canal 6
├── ESP32_03_Deauth_Detector_CH_11/     # Escaneo en canal 11
├── ESP32_04_Deauth_Detector_SCANN/     # Escaneo dinámico en múltiples canales
└── README.md
```

Dentro de cada carpeta:

- `config_template.h`: plantilla con marcadores (placeholders).
- `config.h`: definiciones reales, ignorado por `.gitignore`.
- `main.ino`: código fuente con la lógica de detección y notificación.

## Funcionamiento detallado de los nodos

### Modos de escaneo por canal

- `ESP32_01_Deauth_Detector_CH_01`: monitorea el canal 1.
- `ESP32_02_Deauth_Detector_CH_06`: monitorea el canal 6.
- `ESP32_03_Deauth_Detector_CH_11`: monitorea el canal 11.
- `ESP32_04_Deauth_Detector_SCANN`: escanea los canales 2-5, 7-10 y 12-13.

Cada nodo captura paquetes Wi-Fi, analiza y detecta tramas de desautenticación dirigidas al BSSID objetivo. Al detectar un ataque, genera una alerta y la envía al nodo centralizador.

## Modelo de nodo: ESP32-WROOM-32U

| Característica | Detalle |
| --- | --- |
| Procesador | Dual-core Xtensa 32-bit LX6 a 240 MHz. |
| Memoria | 520 KB de SRAM interna y 4 MB de flash SPI. |
| Wi-Fi | 802.11 b/g/n a 2,4 GHz, con soporte de modo promiscuo. |
| Bluetooth | BLE 4.2 y Bluetooth clásico. El firmware solicita BLE Secure Connections y protección MITM (`ESP_LE_AUTH_REQ_SC_MITM`). |
| Conector U.FL | Permite antenas externas de mayor ganancia. |
| Alimentación | Rango de 2,2 V a 3,6 V. |
| Dimensiones | 18 × 25,5 × 3,1 mm. |

> El firmware solicita BLE Secure Connections y protección MITM mediante `ESP_LE_AUTH_REQ_SC_MITM`. La aplicación efectiva del cifrado y la autenticación depende del proceso de emparejamiento y del cliente BLE. Este comportamiento requiere validación específica en laboratorio.

### Proceso de inicialización

Al arrancar, `main.ino` ejecuta:

1. Monitor serial (115200 baudios) para seguimiento local.
2. Interfaz Wi-Fi en modo estación (`WIFI_STA`).
3. Configuración BLE: `BLEDevice::init("ESP32_[CANAL]")`, servicio con `SERVICE_UUID` y característica *notify* (`CHARACTERISTIC_UUID`), configuración de seguridad con `BLESecurity` (`ESP_LE_AUTH_REQ_SC_MITM`).
4. Registro del callback Wi-Fi: `esp_wifi_set_promiscuous(true)` y `esp_wifi_set_promiscuous_rx_cb(&sniffer_callback)`.

### Detección de tramas de desautenticación

En `sniffer_callback`, el nodo interpreta el paquete recibido, verifica si es una trama de desautenticación y compara el BSSID (`addr3`) con `TARGET_BSSID`. Si coincide, extrae la MAC de origen (`addr2`), la MAC de destino (`addr1`) y el canal (`pkt->rx_ctrl.channel`).

### Construcción y envío de la alerta

Al detectar un ataque, el nodo arma una cadena con los datos del evento, la imprime por el monitor serial y la notifica al cliente BLE conectado mediante `pCharacteristic->setValue(...)` y `pCharacteristic->notify()`.

## Guía de configuración y uso

### 1. Clonar el repositorio

```bash
git clone https://github.com/Eberth-sys/Deauth-Alert-WiFi-IoT-System.git
cd Deauth-Alert-WiFi-IoT-System/perception-layer/esp32-nodes-ino/ESP32_01_Deauth_Detector_CH_01
```

### 2. Preparar el archivo `config.h`

```bash
cp config_template.h config.h
```

Editar `config.h` y reemplazar los valores de ejemplo:

```cpp
#define TARGET_BSSID        "XX:XX:XX:XX:XX:XX"
#define SERVICE_UUID        "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
#define CHARACTERISTIC_UUID "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
```

Confirmar que `config.h` está listado en `.gitignore` antes de compilar.

### 3. Cargar el firmware con Arduino IDE

Este repositorio no incluye configuración de PlatformIO; la vía documentada y probada es Arduino IDE.

1. Abrir `main.ino` desde **Archivo > Abrir** en Arduino IDE.
2. Verificar que la línea `#include "config.h"` esté activa (el archivo debe existir según el paso anterior).
3. En **Herramientas > Placa**, elegir **ESP32 Dev Module**.
4. Configurar en **Herramientas**:
   - Velocidad de carga: 921 600 baudios.
   - Monitor Serial: 115 200 baudios.
   - Partition Scheme: Minimal SPIFFS (1.9 MB APP + 190 KB SPIFFS).
5. Conectar el ESP32 por USB e identificar el puerto serie en **Herramientas > Puerto**.
6. Mantener presionado el botón **BOOT** en el ESP32 y hacer clic en **Subir**.
7. Abrir el Monitor Serial (**Ctrl+Shift+M**) y confirmar los mensajes de arranque y las alertas:

```text
[INFO]  Modo promiscuo activo | Canal: <N>
[ALERT] Origen: ... | Destino: ... | Canal: <N>
```

## Parámetros de configuración recomendados

| Parámetro | Valor |
| --- | --- |
| Placa | ESP32 Dev Module |
| Velocidad de carga | 921 600 baudios |
| Monitor Serial | 115 200 baudios |
| Partition Scheme | Minimal SPIFFS (1.9 MB APP + 190 KB SPIFFS) |
| CPU Frequency | 240 MHz |
| Flash Mode | QIO |
| Flash Frequency | 80 MHz |
| Flash Size | 4 MB (32 Mb) |
| PSRAM | Deshabilitado |
| Core Debug Level | None |
| Erase All Flash Before Sketch Upload | Disabled |
| Events Run On / Arduino Runs On | Core 1 |
| JTAG Adapter | Disabled |
| Zigbee Mode | Disabled |

## Alerta BLE al nodo centralizador

Ejemplo de alerta generada:

```plaintext
[ALERT] Ataque de Deauthentication detectado | Origen: 01:01:01:01:01:01 | Destino: FF:FF:FF:FF:FF:FF | BSSID: 01:01:01:01:01:01 | Canal: 6
```

- **BSSID:** `01:01:01:01:01:01`: el punto de acceso suplantado por el atacante.
- **Origen:** `01:01:01:01:01:01`: coincide con el BSSID suplantado, típico de este ataque.
- **Destino:** `FF:FF:FF:FF:FF:FF`: ataque dirigido a todos los clientes conectados (broadcast).
- **Canal:** `6`: el canal Wi-Fi donde se detectó el ataque.

*(Direcciones MAC de ejemplo; no corresponden a hardware real.)*

## Notas adicionales

- **Uso responsable:** el modo promiscuo debe usarse únicamente en redes donde exista autorización.
- **Seguridad:** el archivo `config.h` está protegido por `.gitignore` para evitar la exposición de información sensible.
- **Compatibilidad Wi-Fi:** este sistema está diseñado para redes Wi-Fi de 2,4 GHz.

## Estado de validación

| Estado de validación |
| :--- |
| Este firmware se probó en laboratorio con hardware real (nodos ESP32-WROOM-32U) y funcionó como parte del prototipo de tesis. |

## Autor

**Esp. Ing. Eberth Gabriel Alarcón González.** Perfil completo, formación y evidencia académica en el [README principal](../../README.md#sobre-el-autor).

## Licencia

Licencia pendiente de definición. Se establecerá antes de la publicación pública definitiva.
