> 🌐 **[English](README.en.md)** · **Español**

# Nodos ESP32 (ESP-IDF): capa de percepción

⬅ Parte de [Deauth-Alert](../../README.md)

<p align="left">
  <img alt="ESP32" src="https://img.shields.io/badge/ESP32-WROOM--32U-E7352C?logo=espressif&logoColor=white">
  <img alt="ESP-IDF" src="https://img.shields.io/badge/ESP--IDF-v5.0%2B-E7352C?logo=espressif&logoColor=white">
  <img alt="BLE" src="https://img.shields.io/badge/Bluetooth-BLE%20seguro-0082FC?logo=bluetooth&logoColor=white">
  <img alt="Licencia" src="https://img.shields.io/badge/licencia-Apache%202.0-blue">
</p>

Manual técnico del firmware ESP-IDF de los nodos ESP32: misma función que la variante Arduino (detección de desautenticación y alerta por BLE), sobre el framework oficial de Espressif.

## Índice

- [Descripción general](#descripción-general)
- [Funcionalidades principales](#funcionalidades-principales)
- [Estructura del trabajo](#estructura-del-trabajo)
- [Arquitectura de los nodos](#arquitectura-de-los-nodos)
- [Modelo de nodo: ESP32-WROOM-32U](#modelo-de-nodo-esp32-wroom-32u)
- [Parámetros de seguridad BLE](#parámetros-de-seguridad-ble)
- [Archivo de particiones](#archivo-de-particiones)
- [Configuración del sistema (sdkconfig.defaults)](#configuración-del-sistema-sdkconfigdefaults)
- [Entorno de trabajo y ejecución](#entorno-de-trabajo-y-ejecución)
- [Alerta BLE al nodo centralizador](#alerta-ble-al-nodo-centralizador)
- [Notas adicionales](#notas-adicionales)
- [Estado de validación](#estado-de-validación)
- [Autor](#autor)
- [Licencia](#licencia)

## Descripción general

Esta carpeta contiene la variante ESP-IDF del firmware de la capa de percepción del sistema Deauth-Alert. Los nodos, basados en microcontroladores ESP32-WROOM-32U, detectan ataques de desautenticación en redes Wi-Fi de 2,4 GHz y envían alertas por Bluetooth Low Energy (BLE) con seguridad configurada a nivel de firmware.

Para el contexto completo del sistema (arquitectura, otras capas, evidencia académica), ver el [README principal](../../README.md).

## Funcionalidades principales

- Captura de paquetes Wi-Fi mediante modo promiscuo.
- Identificación de tramas de desautenticación dirigidas a un BSSID específico.
- Generación de mensajes de alerta con metadatos: origen, destino, BSSID y canal.
- Envío de alertas por BLE con un servicio personalizado y características seguras.
- Configuración de seguridad BLE avanzada (Secure Connections y protección MITM).
- Nodo adicional con capacidad de escaneo dinámico multicanal.

## Estructura del trabajo

```text
perception-layer/espidf-nodes/
├── config/
│   ├── config_template.h
│   └── config.h                        # excluido por .gitignore
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

## Arquitectura de los nodos

| Nodo | Canal analizado | Función | Nombre BLE |
| --- | --- | --- | --- |
| `ESP32_01_Deauth_Detector_CH_01` | Canal 1 | Monitoreo fijo | `ESP32_01_Deauth_Detector_CH_01` |
| `ESP32_02_Deauth_Detector_CH_06` | Canal 6 | Monitoreo fijo | `ESP32_02_Deauth_Detector_CH_06` |
| `ESP32_03_Deauth_Detector_CH_11` | Canal 11 | Monitoreo fijo | `ESP32_03_Deauth_Detector_CH_11` |
| `ESP32_04_Deauth_Detector_SCAN` | Canales 2-5, 7-14 | Escaneo rotativo multicanal | `ESP32_Channel_Scanner` |

Todos los nodos comparten un archivo de configuración común con los parámetros de seguridad y los UUID necesarios para la operación BLE.

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

## Parámetros de seguridad BLE

### Archivo de configuración BLE: `config.h`

1. Ir a la carpeta `config/` del proyecto.
2. Copiar `config_template.h` y renombrarlo como `config.h`.
3. Completar los valores reales:

```c
#define TARGET_BSSID "YOUR_TARGET_BSSID"                  // Dirección MAC del punto de acceso a monitorear
#define SERVICE_UUID "YOUR_SERVICE_UUID"                  // UUID del servicio BLE
#define CHARACTERISTIC_UUID "YOUR_CHARACTERISTIC_UUID"    // UUID de la característica BLE
```

Este archivo es obligatorio para todos los nodos: sin `config.h` presente y completo, el firmware no compila. `config.h` está excluido por `.gitignore`; solo `config_template.h` se versiona.

## Archivo de particiones

`partitions.csv` define cómo se organiza la memoria flash del ESP32:

| Nombre | Tipo | Subtipo | Offset | Tamaño | Descripción |
| --- | --- | --- | --- | --- | --- |
| `nvs` | data | nvs | 0x9000 | 24 KB | Almacenamiento no volátil |
| `phy_init` | data | phy | 0xf000 | 4 KB | Inicialización de hardware PHY |
| `factory` | app | factory | 0x10000 | 1536 KB | Aplicación principal |

## Configuración del sistema (sdkconfig.defaults)

`sdkconfig.defaults` fija la configuración esencial (BLE, seguridad, tabla de particiones), por lo que no hace falta ejecutar `idf.py menuconfig` salvo que se necesiten ajustes adicionales.

| Parámetro | Valor | Descripción |
| --- | --- | --- |
| `CONFIG_BT_ENABLED` | `y` | Habilita el soporte general para Bluetooth. |
| `CONFIG_BT_BLE_ENABLED` | `y` | Activa el soporte específico para BLE. |
| `CONFIG_BT_BLUEDROID_ENABLED` | `y` | Habilita la pila Bluedroid usada por el ESP32. |
| `CONFIG_BT_CONTROLLER_ENABLED` | `y` | Activa el controlador Bluetooth. |
| `CONFIG_BTDM_CONTROLLER_MODE_BLE_ONLY` | `y` | Restringe el modo a BLE (sin Bluetooth clásico). |
| `CONFIG_BT_BLE_SECURE_CONN` | `y` | Habilita conexiones seguras (Secure Connections). |
| `CONFIG_BT_BLE_SMP_ENABLE` | `y` | Activa el protocolo de emparejamiento (SMP). |
| `CONFIG_BT_SMP_ENABLE` | `y` | Compatibilidad con el intercambio de claves de seguridad. |
| `CONFIG_BT_BLE_MAX_ENCRYPTION_KEY_SIZE` | `16` | Longitud máxima de las claves de cifrado BLE. |
| `CONFIG_PARTITION_TABLE_CUSTOM` | `y` | Habilita una tabla de particiones personalizada. |
| `CONFIG_PARTITION_TABLE_CUSTOM_FILENAME` | `../partitions.csv` | Archivo de la tabla personalizada. |
| `CONFIG_PARTITION_TABLE_FILENAME` | `../partitions.csv` | Archivo referenciado como tabla activa. |

## Entorno de trabajo y ejecución

El desarrollo usa ESP-IDF (Espressif IoT Development Framework), versión v5.0 o superior.

### Requisitos previos

- ESP-IDF y una versión de Python compatible con la versión instalada. Se recomienda utilizar el instalador oficial de ESP-IDF.
- Git, para clonar el repositorio.
- Cable USB para conectar el ESP32.

### Comandos para compilar y cargar el firmware

```bash
# Activar el entorno de ESP-IDF
. $HOME/esp/esp-idf/export.sh

# Compilar el proyecto
idf.py build

# Flashear el firmware al dispositivo
idf.py -p /dev/ttyUSB0 flash

# Iniciar el monitor serie
idf.py -p /dev/ttyUSB0 monitor
```

`/dev/ttyUSB0` corresponde al puerto serie en Linux. En Windows suele aparecer como `COM3`, `COM4`, etc.; en macOS, como `/dev/cu.SLAB_USBtoUART`.

### Compilación reproducible con el contenedor oficial (Docker)

Además del entorno local, cada proyecto (uno por nodo) compila de forma reproducible con el **contenedor oficial de Espressif** y **ESP-IDF 5.1** (versión validada **por compilación**), sin instalar la toolchain localmente:

```bash
# Ejemplo reproducible (ESP-IDF 5.1). Ajustar la ruta montada al sistema operativo.
docker run --rm -v <RUTA_espidf-nodes>:/project -w /project/<NODO> espressif/idf:release-v5.1 idf.py set-target esp32 build
```

> **Sintaxis de la ruta montada:** el argumento `-v <ruta>:/project` **varía según el sistema operativo** (las rutas de Windows/PowerShell, Linux y macOS difieren). Adaptar `<RUTA_espidf-nodes>` a la ruta local de `perception-layer/espidf-nodes`.

El build usa el `partitions.csv` de esta carpeta; el binario (~1,09 MB) deja **~31 % libre de la partición de aplicación** (no de toda la memoria flash del ESP32).

## Alerta BLE al nodo centralizador

Ejemplo de alerta generada (contrato JSON v1, `DeauthJson`):

```json
{"v":1,"e":12,"n":"ESP32_1_CH_01","s":"01:01:01:01:01:01","d":"FF:FF:FF:FF:FF:FF","b":"01:01:01:01:01:01","c":1}
```

```json
{"v":1,"e":10,"n":"ESP32_2_CH_06","s":"02:02:02:02:02:02","d":"AA:BB:CC:DD:EE:FF","b":"02:02:02:02:02:02","c":6}
```

- **`v`:** versión del contrato de eventos (`1` en esta versión).
- **`e`:** subtipo de trama de gestión 802.11 — `12` = deauthentication, `10` = disassociation.
- **`n`:** identificador canónico del nodo (`node_id`; ver `devices.yaml.example`).
- **`s`:** dirección de origen reportada, según el mapeo actual.
- **`d`:** dirección de destino reportada (`FF:FF:FF:FF:FF:FF` = broadcast, a todos los clientes).
- **`b`:** BSSID reportado.
- **`c`:** canal Wi-Fi (1–14) en el que se detectó la trama (coherente con el `CH_xx` del `node_id`).

El firmware nuevo emite este JSON v1; la Raspberry Pi conserva un **parser dual** (acepta el JSON nuevo y el texto legacy). El mapeo actual de direcciones (`s`/`d`/`b`) se preserva; su validación semántica final queda pendiente de laboratorio (DT-24).

*(Direcciones MAC de ejemplo; no corresponden a hardware real.)*

## Notas adicionales

- **Uso responsable:** el modo promiscuo debe usarse únicamente en redes donde exista autorización.
- **Seguridad:** el archivo `config.h` está protegido por `.gitignore` para evitar la exposición de información sensible.
- **Compatibilidad Wi-Fi:** este sistema está diseñado para redes Wi-Fi de 2,4 GHz.

## Estado de validación

| Estado de validación |
| :--- |
| **Validación de compilación:** compila de forma reproducible con ESP-IDF 5.1 (contenedor oficial). Esta variante ESP-IDF es una **adaptación académica** y **no** tiene validación física con hardware; la ruta históricamente validada con hardware fue el firmware **Arduino IDE** (misma función; ver el README de la variante Arduino). |

## Autor

**Esp. Ing. Eberth Gabriel Alarcón González.** Perfil completo, formación y evidencia académica en el [README principal](../../README.md#sobre-el-autor).

## Licencia

Código y documentación propia bajo licencia Apache 2.0. Ver [LICENSE](../../LICENSE) y [NOTICE](../../NOTICE) en la raíz del repositorio.
