# Capa de procesamiento

⬅ Parte de [Deauth-Alert](../README.md)

<p align="left">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white">
  <img alt="Raspberry Pi" src="https://img.shields.io/badge/Raspberry%20Pi-OS-A22846?logo=raspberrypi&logoColor=white">
  <img alt="BLE" src="https://img.shields.io/badge/Bluetooth-BLE-0082FC?logo=bluetooth&logoColor=white">
  <img alt="Licencia" src="https://img.shields.io/badge/licencia-pendiente-lightgrey">
</p>

Manual técnico de la capa de procesamiento: recibe las alertas BLE de los nodos ESP32, las persiste en PostgreSQL y las publica hacia AWS IoT y Telegram. Corre en una Raspberry Pi, fuera del conjunto de servicios web en Docker.

## Índice

- [Descripción general](#descripción-general)
- [Nodos ESP32 y su función en la red](#nodos-esp32-y-su-función-en-la-red)
- [Tecnologías utilizadas](#tecnologías-utilizadas)
- [Instalación en Raspberry Pi](#instalación-en-raspberry-pi)
- [Detección de ESP32 mediante Bluetooth](#detección-de-esp32-mediante-bluetooth)
- [Ejecución del proyecto](#ejecución-del-proyecto)
- [Estado de validación](#estado-de-validación)
- [Autor](#autor)
- [Licencia](#licencia)

## Descripción general

Esta capa corre en una Raspberry Pi con Debian 12 (Bookworm) y actúa como unidad de procesamiento central del sistema. Los nodos ESP32 monitorean el tráfico Wi-Fi en sus respectivos canales y, al detectar un ataque de desautenticación, envían una alerta por Bluetooth Low Energy (BLE). Esta capa recibe esas alertas, las procesa, las almacena en PostgreSQL y las publica hacia AWS IoT y Telegram.

Para el contexto completo del sistema (arquitectura, otras capas, evidencia académica), ver el [README principal](../README.md).

## Nodos ESP32 y su función en la red

El sistema cuenta con cuatro nodos ESP32, cada uno anunciado por BLE con un nombre fijo. La capa de procesamiento identifica a cada nodo por ese nombre, definido en `config/devices.yaml`:

| Nombre BLE del nodo | Función |
| --- | --- |
| `ESP32_1_CH_01` | Monitorea el canal 1. |
| `ESP32_2_CH_06` | Monitorea el canal 6. |
| `ESP32_3_CH_11` | Monitorea el canal 11. |
| `ESP32_4_SCANN` | Escanea los canales 2-5, 7-10 y 12-13. |

Cada ESP32 captura los paquetes Wi-Fi en su canal y, si detecta un posible ataque de desautenticación, envía una alerta a la Raspberry Pi por BLE.

## Tecnologías utilizadas

### Hardware

| Componente | Descripción |
| --- | --- |
| Raspberry Pi 5 (8 GB RAM) | Unidad central de procesamiento, ejecuta esta capa en Debian 12 (Bookworm). |
| ESP32-WROOM-32U | Módulo con conectividad Wi-Fi 2,4 GHz y BLE, con antena externa. |

### Software

| Tecnología | Versión | Descripción |
| --- | --- | --- |
| Python | 3.11 | Incluido por defecto en Debian 12 (Bookworm); versión usada en el desarrollo. |
| BlueZ | Stack del sistema | Pila Bluetooth de Linux para gestionar las conexiones BLE. |
| Bleak | Sin versión fijada | Librería de Python para la comunicación con dispositivos BLE. |
| PyYAML | Sin versión fijada | Lectura de `devices.yaml`. |
| asyncio | Incluido en Python 3 | Tareas asíncronas para el procesamiento en tiempo real. |

> Las dependencias de Python (`requirements.txt`) no están fijadas por versión; se instala la última disponible al momento de la instalación. Fijarlas es una mejora pendiente.

## Instalación en Raspberry Pi

### 1. Instalar el sistema operativo

1. Descargar Raspberry Pi OS (Debian 12, Bookworm) desde [raspberrypi.com/software](https://www.raspberrypi.com/software/).
2. Grabar la imagen en una tarjeta SD con Raspberry Pi Imager.
3. Configurar SSH y Wi-Fi para acceso remoto (opcional).

### 2. Acceder a la Raspberry Pi por SSH

```bash
ssh pi@<IP_DE_LA_RASPBERRY_PI>
```

### 3. Actualizar el sistema e instalar dependencias

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install git python3 python3-pip python3-venv bluetooth bluez -y
```

| Paquete | Rol |
| --- | --- |
| `git` | Clonar el repositorio. |
| `python3`, `python3-pip`, `python3-venv` | Ejecutar el proyecto en un entorno virtual. |
| `bluetooth`, `bluez` | Gestionar las conexiones BLE en la Raspberry Pi. |

### 4. Clonar el repositorio

```bash
cd ~
git clone https://github.com/Eberth-sys/Deauth-Alert-WiFi-IoT-System.git
cd Deauth-Alert-WiFi-IoT-System/processing-layer
```

> El repositorio ya contiene esta capa dentro de la carpeta `processing-layer/`; no hace falta cambiar de rama.

### 5. Crear y activar un entorno virtual

```bash
python3 -m venv ble
source ble/bin/activate
```

El prompt de la terminal debería mostrar el entorno activo, por ejemplo `(ble) pi@raspberrypi:~/Deauth-Alert-WiFi-IoT-System/processing-layer $`.

### 6. Instalar las dependencias

```bash
pip install -r requirements.txt
```

## Detección de ESP32 mediante Bluetooth

Para comprobar que los ESP32 anuncian su presencia por BLE:

```bash
bluetoothctl
scan on
```

Salida esperada:

```
[NEW] Device AA:BB:CC:DD:EE:FF ESP32_1_CH_01
[NEW] Device 11:22:33:44:55:66 ESP32_2_CH_06
```

Si los dispositivos aparecen en la lista, están listos para la conexión.

### Solución de problemas

Si Bluetooth no detecta los ESP32, confirmar que estén encendidos y con el firmware cargado. Si el problema persiste:

```bash
sudo systemctl restart bluetooth
bluetoothctl
scan on
```

Ante problemas de permisos, agregar el usuario al grupo `bluetooth` y reiniciar:

```bash
sudo usermod -aG bluetooth pi
sudo reboot
```

## Ejecución del proyecto

### 1. Configurar `devices.yaml`

Copiar la plantilla y completarla con las direcciones MAC reales de los ESP32 y los UUID del servicio BLE:

```bash
cp config/devices.yaml.example config/devices.yaml
nano config/devices.yaml
```

```yaml
# Reemplazar las direcciones MAC y los UUID con los valores reales antes de ejecutar el sistema.

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

### 2. Ejecutar el script principal

```bash
python main.py
```

Salida esperada:

```
[INFO] Buscando ESP32_1_CH_01...
[CONNECTED] Conectado a ESP32_1_CH_01
[INFO] Esperando datos de ESP32_1_CH_01...
```

## Estado de validación

| Estado de validación |
| :--- |
| Esta capa se probó en laboratorio con hardware real (nodos ESP32 y Raspberry Pi) y funcionó como parte del prototipo de tesis. Las dependencias de Python no están fijadas por versión; fijarlas es una mejora pendiente documentada en el README principal. |

## Autor

**Esp. Ing. Eberth Gabriel Alarcón González.** Perfil completo, formación y evidencia académica en el [README principal](../README.md#sobre-el-autor).

## Licencia

Licencia pendiente de definición. Se establecerá antes de la publicación pública definitiva.
