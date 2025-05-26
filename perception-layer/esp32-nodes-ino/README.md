# 📡 Nodos IoT ESP32 para monitoreo y detección de ataques de desautenticación en redes Wi‑Fi 2,4 GHz  <!-- omit in toc -->

## 🗂️ Índice <!-- omit in toc -->

<!-- TOC levels="2..4" -->

- [🛡️ Capa de Percepción (Arduino IDE)](#🛡️-capa-de-percepción-arduino-ide)
- [⚙️ Estructura del proyecto](#⚙️-estructura-del-proyecto)
- [📡 Funcionamiento detallado de los nodos](#📡-funcionamiento-detallado-de-los-nodos)
  - [🕹️ Modos de Escaneo por Canal](#🕹️-modos-de-escaneo-por-canal)
  - [🔌 Modelo de nodo: ESP32-WROOM-32U](#-Modelo-de-nodo:-ESP32-WROOM-32U)
  - [1️⃣ Proceso de inicialización](#1️⃣-proceso-de-inicialización)
  - [2️⃣ Modo promiscuo](#2️⃣-modo-promiscuo)
  - [3️⃣ Detección de paquetes deauth](#3️⃣-detección-de-paquetes-deauth)
  - [4️⃣ Construcción y envío de alerta BLE](#4️⃣-construcción-y-envío-de-alerta-ble)
- [🚀 Guía de configuración y uso](#🚀-guía-de-configuración-y-uso)
  - [A. Clonar el repositorio](#a-clonar-el-repositorio)
  - [B. Preparar el Archivo `config.h`](#b-preparar-el-archivo-configh)
  - [C. Carga con PlatformIO (VSCode)](#c-carga-con-platformio-vscode)
  - [D. Carga con Arduino IDE](#d-carga-con-arduino-ide)
- [🌟🔧 Parámetros críticos de configuración](#🌟🔧-parámetros-críticos-de-configuración)
- [⚡ Otros ajustes](#⚡-otros-ajustes)
- [📲 Alerta BLE al Nodo Centralizador](#📲-alerta-ble-al-nodo-centralizador)
  - [⚡ Ejemplo de alerta generada](#⚡-ejemplo-de-alerta-generada)
  - [Desglose del ejemplo](#desglose-del-ejemplo)
- [📖 Notas adicionales](#📖-notas-adicionales)
- [👨‍💻 Autor](#👨‍💻-autor)
- [📄 Licencia](#📄-licencia)
<!-- /TOC -->
---

## 🛡️ **Capa de Percepción (Arduino IDE)**

Este repositorio contiene el código fuente para los **nodos IoT ESP32** del proyecto de grado:
**"Sistema IoT para el Monitoreo y Detección de Ataques de Desautenticación en Redes Wi‑Fi"**.

Estos nodos ESP32 son responsables de escanear redes Wi‑Fi de **2.4 GHz** en busca de posibles **ataques de desautenticación**, capturando paquetes en modo promiscuo y enviando alertas a un **nodo centralizador BLE** (Gateway IoT) para su posterior análisis y gestión de eventos.

---

## ⚙️ Estructura del proyecto

Cada nodo se aloja en una carpeta independiente bajo `esp32-nodes-ino/`:

```text
DEAUTH-ALERT-WIFI-IOT-SYSTEM
│
esp32-nodes-ino/
├── ESP32_01_Deauth_Detector_CH_01/     
│   ├── config_template.h               # Plantilla para configuración
│   ├── config.h                        # excluido por .gitignore
│   └── main.ino                        # Escaneo en canal 1
├── ESP32_02_Deauth_Detector_CH_06/     
│   ├── config_template.h               # Plantilla para configuración
│   ├── config.h                        # excluido por .gitignore
│   └── main.ino                        # Escaneo en canal 6
├── ESP32_03_Deauth_Detector_CH_11/     
│   ├── config_template.h               # Plantilla para configuración
│   ├── config.h                        # excluido por .gitignore
│   └── main.ino                        # Escaneo en canal 11
├── ESP32_04_Deauth_Detector_SCANN/     
│   ├── config_template.h               # Plantilla para configuración
│   ├── config.h                        # excluido por .gitignore
│   └── main.ino                        # Escaneo dinámico en múltiples canales
└── README.md                           # 📄 README ESP32 iot-nodes
```

Dentro de cada carpeta:

* 📄 `config_template.h`: plantilla con marcadores (placeholders).
* 🔒 `config.h`: definiciones reales (ignorado por `.gitignore`).
* 💻 `main.ino`: código fuente con lógica de detección y notificación.

---

## 📡 Funcionamiento detallado de los nodos

### 🕹️ Modos de Escaneo por Canal

1. **Códigos Individuales por Canal:**

   * `ESP32_ch_01` 🎯 Monitorea el canal 1.
   * `ESP32_ch_06` 🎯 Monitorea el canal 6.
   * `ESP32_ch_11` 🎯 Monitorea el canal 11.
   * `ESP32_ch_Scan` 🔄 Escanea canales 2-5, 7-10 y 12-13.

2. **Detección de Ataques de Desautenticación:**

   * Los nodos IoT ESP32 capturan paquetes Wi‑Fi, analizan y detectan paquetes de desautenticación dirigidos al BSSID objetivo.
   * Al detectar un ataque, el nodo genera una alerta y la envía al nodo centralizador para su posterior análisis y gestión de eventos.
---

### 🔌 Modelo de nodo: ESP32-WROOM-32U

Cada nodo está basado en el ESP32-WROOM-32U, un módulo compacto y potente que integra Wi-Fi y Bluetooth para capturar, procesar y transmitir datos de manera eficiente. A continuación, sus principales características:

| Característica            | Detalle                                                                                                       |
|---------------------------|----------------------------------------------------------------------------------------------------------------|
| 🖥️ **Procesador**         | Dual-core Xtensa® 32-bit LX6 a 240 MHz, alto rendimiento para captura y análisis de paquetes.                |
| 💾 **Memoria**            | 520 KB de SRAM interna y 4 MB de flash SPI, suficiente para firmware y buffers de datos.                       |
| 📶 **Wi-Fi**              | 802.11 b/g/n a 2,4 GHz, compatible con modo promiscuo, esencial para detección pasiva de tramas de gestión.   |
| 🔵 **Bluetooth**          | BLE 4.2 y Bluetooth clásico, usado en este proyecto para transmisión cifrada de alertas.                      |
| 📡 **Conector U.FL**      | Permite acoplar antenas externas de alta ganancia, mejorando la recepción en entornos con interferencias.     |
| 🔋 **Alimentación**       | Rango de 2,2 V a 3,6 V, adecuado para baterías o fuentes de alimentación embebidas.                           |
| 📏 **Dimensiones**        | 18 × 25,5 × 3,1 mm, facilita su integración en carcasas y entornos reducidos.                                 |

📸 **Referencia de imagen**:  

[![esp32-wroom32u.png](https://i.postimg.cc/W1V2Zsxj/esp32-wroom32u.png)](https://postimg.cc/jL800Ysk)

---
### 1️⃣ Proceso de inicialización

Al arrancar, `main.ino` ejecuta:

1. **Monitor Serial** (115200 baud) para seguimiento local.
2. **Interfaz Wi‑Fi** en modo estación (`WIFI_STA`).
3. **Configuración BLE**:

   * `BLEDevice::init("ESP32_[CANAL]")`.
   * Servicio BLE con `SERVICE_UUID` y característica **notify** (`CHARACTERISTIC_UUID`).
   * Callbacks de conexión/desconexión para reiniciar advertising.
4. **Registro de Callback Wi‑Fi**:

   * `esp_wifi_set_promiscuous(true)`.
   * `esp_wifi_set_promiscuous_rx_cb(&sniffer_callback)`.

### 2️⃣ Modo promiscuo

Captura **todos** los paquetes en el canal seleccionado:

```cpp
esp_wifi_set_promiscuous(true);
esp_wifi_set_promiscuous_rx_cb(&sniffer_callback);
```

Permite:

* 📋 Análisis exhaustivo de la actividad de red.
* ✂️ Filtrado específico de paquetes de desautenticación.

### 3️⃣ Detección de paquetes deauth

En `sniffer_callback`:

1. Interpretación del paquete:

   ```cpp
   wifi_promiscuous_pkt_t *pkt = (wifi_promiscuous_pkt_t *)buf;
   wifi_ieee80211_packet_t *ipkt = (wifi_ieee80211_packet_t *)pkt->payload;
   ```
2. Verificación de **Deauth**.
3. Comparación de **BSSID** (`addr3`) con `TARGET_BSSID`.
4. Extracción de:

   * 🆔 **MAC origen** (`addr2`).
   * 🆔 **MAC destino** (`addr1`).
   * 📶 **Canal** (`pkt->rx_ctrl.channel`).

### 4️⃣ Construcción y envío de alerta BLE

Al detectar un ataque:

1. Generar cadena:

   ```cpp
   String alert = "[ALERT] Ataque de Deauthentication detectado | Origen: " + macOrigen + " | Destino: " + macDestino + " | BSSID: " + bssidStr + " | Canal: " + channel;
   ```
2. Imprimir en **Serial**.
3. Notificar cliente BLE conectado:

   ```cpp
   pCharacteristic->setValue(alert.c_str());
   pCharacteristic->notify();
   ```

El evento se transmite en tiempo real al nodo centralizador.

---

## 🚀 Guía de configuración y uso

### A. Clonar el repositorio

```bash
git clone https://github.com/Eberth-sys/Deauth-Alert-WiFi-IoT-System.git
cd Deauth-Alert-WiFi-IoT-System/esp32-nodes-ino/ESP32_01_Deauth_Detector_CH_01
```

### B. Preparar el Archivo `config.h`

1. `cp config_template.h config.h`
2. Reemplazar placeholders:

   ```cpp
   #define TARGET_BSSID        "AA:BB:CC:DD:EE:FF"
   #define SERVICE_UUID        "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
   #define CHARACTERISTIC_UUID "yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy"
   ```
3. Confirmar `config.h` en `.gitignore`.

### C. Carga con PlatformIO (VSCode)

Para distribuir el firmware en los nodos ESP32 desde Visual Studio Code con PlatformIO, se recomienda el siguiente procedimiento detallado:

1. **Abrir el proyecto**

   * En VSCode, seleccionar **Archivo > Abrir carpeta** y navegar hasta la ruta del nodo deseado, por ejemplo:

     ```text
     Deauth-Alert-WiFi-IoT-System/esp32-nodes-ino/ESP32_01_Deauth_Detector_CH_01
     ```

2. \*\*Verificar \*\***`platformio.ini`**

   * Confirmar que la sección `[env]` corresponde al modelo de placa ESP32 utilizado:

     ```ini
     [env:esp32dev]
     platform = espressif32
     board    = esp32dev
     framework = arduino
     ```
   * Ajustar puertos y velocidad si fuera necesario (opcional):

     ```ini
     upload_port = COM3        ; o /dev/ttyUSB0
     upload_speed = 921600     ; velocidad en baudios
     ```

3. **Compilar el firmware**

   * Ejecutar el comando **Build** (icono ✔️ o `PlatformIO: Build`) para comprobar que no haya errores de compilación.
   * Revisar la consola de VSCode para asegurarse de que todos los archivos `.cpp` y `.ino` se procesan correctamente.

4. **Subir el firmware al dispositivo**

   * Conectar el ESP32 al equipo via USB.
   * Pulsar **Upload** (icono ➤ o `PlatformIO: Upload`) para flashear el dispositivo.
   * Durante la operación, observar en la consola:

     ```text
     [SUCCESS] Firmware fue cargado correctamente en /dev/ttyUSB0
     ```

5. **Verificar la ejecución**

   * Abrir **Monitor Serial** (`PlatformIO: Serial Monitor`) o pulsar el icono de plug 🔌.
   * Configurar velocidad en **115200 baudios**.
   * Confirmar mensajes de arranque y alertas en tiempo real:

     ```plaintext
     [INFO]  Modo promiscuo activo | Canal: 6
     [INFO]  Servidor BLE listo
     [ALERT] Origen: … | Destino: … | Canal: 6
     ```

Con estos pasos, PlatformIO facilita la compilación, carga y monitoreo centralizado del firmware de los nodos ESP32.

### D. 🚀 Carga con Arduino IDE 🖥️

La carga del firmware mediante Arduino IDE sigue estos pasos detallados para asegurar un despliegue exitoso:

1. \*\*Abrir el sketch \*\***`main.ino`**

   * Desde Arduino IDE, ir a **Archivo > Abrir** y seleccionar `main.ino` del nodo correspondiente.

2. **Preparar las definiciones de configuración**

   * Comentar la línea que incluye el archivo de configuración (uso en PlatformIO):

     ```cpp
     // #include "config.h"
     ```
   * Insertar manualmente al inicio las directivas con los valores reales:

     ```cpp
     #define TARGET_BSSID        "AA:BB:CC:DD:EE:FF"
     #define SERVICE_UUID        "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
     #define CHARACTERISTIC_UUID "yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy"
     ```

3. **Seleccionar placa y ajustes de compilación**

   * En **Herramientas > Placa**, elegir **ESP32 Dev Module**.
   * Configurar en **Herramientas** los siguientes parámetros:

     * **Velocidad de carga:** `921600 baudios`
     * **Monitor Serial:** `115200 baudios`
     * **Partition Scheme:** `Minimal SPIFFS (1.9MB APP + 190KB SPIFFS)`

4. **Conectar y preparar el ESP32**

   * Enchufar el ESP32 al puerto USB del equipo.
   * Identificar el **Puerto serie** en **Herramientas > Puerto**.

5. **Subir el sketch**

   * Mantener pulsado el botón **BOOT** en el ESP32.
   * Hacer clic en **Herramientas > Subir** o en el icono de flecha (➤).
   * Observar en la consola de Arduino IDE la confirmación de carga exitosa:

     ```text
     Procesando sketch...
     Subido con éxito al puerto COM3
     ```

6. **Verificar la ejecución**

   * Abrir **Monitor Serial** (**Ctrl+Shift+M**).
   * Confirmar que aparecen los mensajes de inicio y las alertas:

     ```plaintext
     [INFO]  Modo promiscuo activo | Canal: <N>
     [ALERT] Origen: … | Destino: … | Canal: <N>
     ```

---

## 🌟🔧 Parámetros críticos de configuración 🔧🌟

> A continuación, se destacan los parámetros esenciales para el correcto funcionamiento de los nodos ESP32 en Arduino IDE:

| ⚙️ **Parámetro**         | ✅ **Valor recomendado**                     |
| ------------------------ | ------------------------------------------- |
| 🖥️ Placa                | ESP32 Dev Module                            |
| 🚀 Velocidad de carga    | 921 600 baudios                             |
| 🔌 Monitor Serial        | 115 200 baudios                             |
| 💾 Scheme de particiones | ⚠️`Minimal SPIFFS (1.9 MB APP + 190 KB SPIFFS)⚠️` |
| ⚡ CPU Frequency          | 240 MHz                                     |
| 🔧 Flash Mode            | QIO                                         |
| 📦 Flash Size            | 4 MB                                        |
| 🧠 PSRAM                 | Deshabilitado                               |

---

## ⚡ Otros ajustes 🛠️

> Estos ajustes ofrecen un control más fino sobre el rendimiento y comportamiento del ESP32:

| ⚙️ **Parámetro**                             | 🔢 **Configuración Recomendada** |
| -------------------------------------------- | -------------------------------- |
| 🔄 **CPU Frequency**                         | 240 MHz (Wi‑Fi/BT)               |
| 🐞 **Core Debug Level**                      | None                             |
| 🗑️ **Erase All Flash Before Sketch Upload** | Disabled                         |
| 🏷️ **Events Run On**                        | Core 1                           |
| 🔊 **Flash Frequency**                       | 80 MHz                           |
| 🔧 **Flash Mode**                            | QIO                              |
| 💾 **Flash Size**                            | 4 MB (32 Mb)                     |
| 🔌 **JTAG Adapter**                          | Disabled                         |
| ⚙️ **Arduino Runs On**                       | Core 1                           |
| 🧠 **PSRAM**                                 | Disabled                         |
| 📡 **Zigbee Mode**                           | Disabled                         |

---

## 📲 Alerta BLE al Nodo Centralizador

### ⚡ **Ejemplo de alerta generada:**

```plaintext
[ALERT] Ataque de Deauthentication detectado | Origen: 01:01:01:01:01:01 | Destino: FF:FF:FF:FF:FF:FF | BSSID: 01:01:01:01:01:01 | Canal: 6
```

#### Desglose del ejemplo:
- 🛡️**BSSID:** `01:01:01:01:01:01` → El punto de acceso suplantado por el atacante.  
- 👉**Origen:** `01:01:01:01:01:01` → Coincide con el BSSID suplantado, típico en estos ataques.  
- 🎯**Destino:** `FF:FF:FF:FF:FF:FF` → Ataque dirigido a **todos** los clientes conectados al punto de acceso (broadcast).  
- 📶**Canal:** `6` → El canal Wi-Fi donde se detectó el ataque.

El nodo centralizador realiza:

1. 💾 Registro en base de datos.
2. 📈 Procesamiento de tendencias.
3. 📊 Generación de reportes.
4. 🚨 Notificación a sistemas de seguridad.

---

## 📖 **Notas adicionales**

- ⚠️ **Uso responsable:**  
  El modo promiscuo debe usarse únicamente en redes donde tengas autorización.

- 🔒 **Seguridad:**  
  El archivo `config.h` está protegido mediante `.gitignore` para evitar la exposición de información sensible.

- 📡 **Compatibilidad Wi-Fi:**  
  Este sistema está diseñado para redes Wi-Fi de **2.4 GHz**.

---

## 👨‍💻 **Autor**

**Esp. Ing. Eberth Alarcón**  
🌐 [LinkedIn - Eberth Alarcón](https://www.linkedin.com/in/eberthalarcon90)  

**Universidad de Buenos Aires (UBA)** 🇦🇷  
**Facultad de Ingeniería**  -  **Especialización en Internet de las Cosas (IoT)**

<img src="https://i.postimg.cc/nz9jwWQG/uba-logo.png" alt="Universidad de Buenos Aires" width="300"/>

---

## 📄 Licencia

Proyecto bajo **Licencia MIT** (ver `LICENSE.md`).

---
