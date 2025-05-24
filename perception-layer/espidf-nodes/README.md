# 📡 Nodos IoT ESP32 para monitoreo y detección de ataques de desautenticación en redes Wi‑Fi 2,4 GHz<!-- omit in toc -->

## 🗂️ Índice <!-- omit in toc -->

<!-- TOC levels="2..4" -->

- [🛠️ Entorno de trabajo y ejecución](#️-entorno-de-trabajo-y-ejecución)
    - [📋 Requisitos previos](#-requisitos-previos)
    - [🧪 Comandos para compilar y cargar el firmware](#-comandos-para-compilar-y-cargar-el-firmware)
  - [📲 Alerta BLE al nodo centralizador](#-alerta-ble-al-nodo-centralizador)
    - [⚡ **Ejemplo de alerta generada:**](#-ejemplo-de-alerta-generada)
      - [Desglose del ejemplo:](#desglose-del-ejemplo)
  - [📖 **Notas adicionales**](#-notas-adicionales)
  - [👨‍💻 **Autor**](#-autor)
  - [📄 Licencia](#-licencia)

## 🧩 Descripción General

La presente documentación corresponde a la **capa de percepción** del sistema de ciberseguridad denominado *Deauth-Alert WiFi IoT System*. Esta capa está constituida por una serie de nodos desarrollados sobre microcontroladores **ESP32**, cuyo propósito es detectar ataques de desautenticación en redes Wi-Fi de 2,4 GHz y emitir alertas cifradas a través de tecnología **Bluetooth Low Energy (BLE)**.

Dichos ataques, conocidos como *deauthentication attacks*, forman parte de técnicas comunes en escenarios de denegación de servicio (DoS) en redes inalámbricas. Este sistema proporciona una respuesta efectiva y distribuida, al desplegar nodos que monitorizan diferentes canales del espectro Wi-Fi.

## ⚙️ Funcionalidades principales

- Captura de paquetes Wi-Fi mediante el modo promiscuo.
- Identificación de tramas de desautenticación dirigidas a un BSSID específico.
- Generación de mensajes de alerta con metadatos: origen, destino, BSSID y canal.
- Envío de alertas por BLE utilizando un servicio personalizado con características seguras.
- Configuración de seguridad BLE avanzada (Secure Connections + MITM).
- Nodo adicional con capacidad de escaneo dinámico multicanal.

## 🗂️ Estructura del trabajo

```bash
perception-layer/
├── esp32-nodes-ino/
├── espidf-nodes/
│   ├── config/
│   │   ├── config_template.h
│   │   └── config.h
│   ├── ESP32_01_Deauth_Detector_CH_01/
│   │   ├── main/
│   │   │   ├── CMakeLists.txt
│   │   │   └── main.c
│   │   ├── CMakeLists.txt
│   │   └── sdkconfig.defaults
│   ├── ESP32_02_Deauth_Detector_CH_06/
│   │   ├── main/
│   │   │   ├── CMakeLists.txt
│   │   │   └── main.c
│   │   ├── CMakeLists.txt
│   │   └── sdkconfig.defaults
│   ├── ESP32_03_Deauth_Detector_CH_11/
│   │   ├── main/
│   │   │   ├── CMakeLists.txt
│   │   │   └── main.c
│   │   ├── CMakeLists.txt
│   │   └── sdkconfig.defaults
│   ├── ESP32_04_Deauth_Detector_SCAN/
│   │   ├── main/
│   │   │   ├── CMakeLists.txt
│   │   │   └── main.c
│   │   ├── CMakeLists.txt
│   │   └── sdkconfig.defaults
│   ├── partitions.csv
│   └── README.md

```

## 🧠 Arquitectura de los nodos

La arquitectura comprende cuatro nodos independientes, cada uno dedicado a analizar un canal específico o múltiples canales, según el siguiente esquema:

| Nodo                             | Canal Analizado  | Función                     | Nombre BLE                       |
| -------------------------------- | ---------------- | --------------------------- | -------------------------------- |
| `ESP32_01_Deauth_Detector_CH_01` | Canal 1          | Monitoreo fijo              | `ESP32_01_Deauth_Detector_CH_01` |
| `ESP32_02_Deauth_Detector_CH_06` | Canal 6          | Monitoreo fijo              | `ESP32_02_Deauth_Detector_CH_06` |
| `ESP32_03_Deauth_Detector_CH_11` | Canal 11         | Monitoreo fijo              | `ESP32_03_Deauth_Detector_CH_11` |
| `ESP32_04_Deauth_Detector_SCAN`  | Canales 2-5,7-14 | Escaneo rotativo multicanal | `ESP32_Channel_Scanner`          |

Todos los nodos comparten un archivo de configuración común con los parámetros de seguridad y las direcciones UUID necesarias para la operación BLE.

 **Detección de ataques de desautenticación:**

   * Los nodos IoT ESP32 capturan paquetes Wi‑Fi, analizan y detectan paquetes de desautenticación dirigidos al BSSID objetivo.
   * Al detectar un ataque, el nodo genera una alerta y la envía al nodo centralizador para su posterior análisis y gestión de eventos.
  
## 🔐 Parámetros de seguridad BLE

### 🛠️ Archivo de configuración BLE: `config.h`

Para que el sistema funcione correctamente, es necesario crear un archivo personalizado con los parámetros reales del entorno BLE. A continuación, se detallan los pasos a seguir:

1. Dirígete a la carpeta `config/` del proyecto.
2. Localiza el archivo `config_template.h`.
3. Copia este archivo y renómbralo como `config.h`.
4. Abre `config.h` y reemplaza los siguientes valores por los que correspondan a tu caso específico:

```c
#define TARGET_BSSID "XX:XX:XX:XX:XX:XX"                            // Dirección MAC del punto de acceso (AP) a monitorear
#define SERVICE_UUID "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"         // UUID del servicio BLE
#define CHARACTERISTIC_UUID "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"  // UUID de la característica BLE
````

🔎 Este archivo es obligatorio para todos los nodos ESP32, ya que contiene:

* El identificador del **BSSID objetivo**.
* Los **UUIDs** necesarios para establecer una comunicación BLE segura con el cliente central (como una Raspberry Pi).

⚠️ **Importante**: Si el archivo `config.h` no está presente o está mal configurado, el firmware no podrá compilar ni funcionar correctamente.


## 🧱 Archivo de particiones

El archivo partitions.csv define cómo se organiza la memoria flash del ESP32. Es necesario para que el sistema pueda identificar correctamente las áreas reservadas para la aplicación, los datos persistentes (NVS) y la configuración del hardware. Este archivo permite al firmware funcionar de forma estructurada y evita conflictos en el uso del espacio de memoria.

| Nombre     | Tipo | Subtipo | Offset  | Tamaño  | Descripción                    |
| ---------- | ---- | ------- | ------- | ------- | ------------------------------ |
| `nvs`      | data | nvs     | 0x9000  | 24 KB   | Almacenamiento no volátil      |
| `phy_init` | data | phy     | 0xf000  | 4 KB    | Inicialización de hardware PHY |
| `factory`  | app  | factory | 0x10000 | 1536 KB | Aplicación principal           |

## ⚙️ Configuración del sistema (`sdkconfig.defaults`)

El archivo `sdkconfig.defaults` incluye las configuraciones esenciales para el funcionamiento del sistema, como el soporte para BLE, la seguridad requerida y la tabla de particiones personalizada. Gracias a esto, no es necesario ejecutar idf.py menuconfig, salvo que se requieran otras modificaciones específicas.

### 🔧 Parámetros de configuración BLE

| Parámetro                              | Valor | Descripción                                                                 |
|----------------------------------------|-------|-----------------------------------------------------------------------------|
| `CONFIG_BT_ENABLED`                    | `y`   | Habilita el soporte general para Bluetooth.                                |
| `CONFIG_BT_BLE_ENABLED`                | `y`   | Activa el soporte específico para Bluetooth Low Energy.                    |
| `CONFIG_BT_BLUEDROID_ENABLED`          | `y`   | Habilita la pila Bluedroid de Bluetooth utilizada por el ESP32.            |
| `CONFIG_BT_CONTROLLER_ENABLED`         | `y`   | Activa el controlador Bluetooth en el dispositivo.                         |
| `CONFIG_BTDM_CONTROLLER_MODE_BLE_ONLY` | `y`   | Define que solo se utilizará BLE (no Bluetooth Clásico).                   |

### 🔐 Seguridad BLE

| Parámetro                           | Valor | Descripción                                                                 |
|-------------------------------------|-------|-----------------------------------------------------------------------------|
| `CONFIG_BT_BLE_SECURE_CONN`         | `y`   | Habilita conexiones seguras (Secure Connections) con BLE.                  |
| `CONFIG_BT_BLE_SMP_ENABLE`          | `y`   | Activa el protocolo de emparejamiento BLE (SMP: Security Manager Protocol).|
| `CONFIG_BT_SMP_ENABLE`              | `y`   | Asegura compatibilidad total con el intercambio de claves de seguridad.    |
| `CONFIG_BT_BLE_MAX_ENCRYPTION_KEY_SIZE` | `16` | Define la longitud máxima permitida para las claves de cifrado BLE.       |

### 🧱 Configuración de particiones

| Parámetro                                  | Valor               | Descripción                                                      |
|--------------------------------------------|---------------------|------------------------------------------------------------------|
| `CONFIG_PARTITION_TABLE_CUSTOM`            | `y`                 | Permite definir una tabla de particiones personalizada.          |
| `CONFIG_PARTITION_TABLE_CUSTOM_FILENAME`   | `../partitions.csv` | Archivo donde se encuentra dicha tabla personalizada.            |
| `CONFIG_PARTITION_TABLE_FILENAME`          | `../partitions.csv` | Archivo referenciado como tabla activa de particiones.           |

---
# 🛠️ Entorno de trabajo y ejecución

Para el desarrollo, compilación y carga del firmware del sistema IoT, se utiliza el entorno **ESP-IDF (Espressif IoT Development Framework)**. Se recomienda utilizar la versión **v5.0 o superior** para asegurar la compatibilidad con las herramientas y bibliotecas necesarias.

ESP-IDF es el marco de desarrollo oficial para los microcontroladores ESP32, y proporciona una colección robusta de herramientas, bibliotecas, ejemplos y documentación para facilitar el desarrollo de aplicaciones embebidas de manera eficiente y profesional.

### 📋 Requisitos previos

Antes de proceder, asegúrese de tener instalado lo siguiente:

- **Python 3.7 o superior** – requerido para ejecutar scripts y herramientas del entorno.
- **Git** – utilizado para clonar el repositorio oficial del proyecto y gestionar versiones.
- **Herramientas del ESP-IDF** – pueden instalarse automáticamente mediante el instalador oficial (disponible para Windows, macOS y Linux) o manualmente siguiendo la guía de instalación.
- **Cable USB** – necesario para conectar el microcontrolador ESP32 al computador desde el cual se cargará el firmware.

### 🧪 Comandos para compilar y cargar el firmware

Los siguientes comandos deben ejecutarse en una terminal para preparar el entorno de desarrollo, compilar el proyecto y cargar el firmware al ESP32:

```bash
# Activar el entorno del ESP-IDF
. $HOME/esp/esp-idf/export.sh

# Compilar el proyecto
idf.py build

# Flashear el firmware al dispositivo ESP32
idf.py -p /dev/ttyUSB0 flash

# Iniciar el monitor en serie para ver los mensajes del ESP32 en tiempo real
idf.py -p /dev/ttyUSB0 monitor
```

🔧 **Nota:** El valor `/dev/ttyUSB0` corresponde al puerto de comunicación del ESP32 en sistemas basados en Linux. En **Windows**, puede aparecer como `COM3`, `COM4`, etc. En **macOS**, puede ser algo como `/dev/cu.SLAB_USBtoUART`. Es indispensable identificar correctamente este puerto antes de continuar.

📌 Estos pasos permiten compilar el firmware, cargarlo en el microcontrolador y supervisar su funcionamiento en tiempo real mediante un monitor serial, lo cual es crucial para verificar la correcta ejecución del sistema y depurar errores durante la etapa de desarrollo.


----

## 📲 Alerta BLE al nodo centralizador

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