
# 🖥️ **Capa de Procesamiento IoT - Sistema de monitoreo y detección de ataques de desautenticación en redes Wi-Fi 2.4 GHz**  

## 📌 **Descripción General**  

Este repositorio contiene la implementación y desarrollo de la **Capa de Procesamiento** del **Sistema IoT para el Monitoreo y Detección de Ataques de Desautenticación en Redes Wi-Fi 2.4 GHz**.  

El sistema está compuesto por **nodos ESP32-WROOM-32U**, encargados de capturar y analizar el tráfico Wi-Fi en diferentes canales, y una **Raspberry Pi con Debian 12 (Bookworm)** que actúa como unidad de procesamiento central.  

📡 **Funcionamiento:**  
- Los **ESP32** monitorean paquetes Wi-Fi en sus respectivos canales y detectan posibles **ataques de desautenticación**.  
- Cuando se detecta una anomalía, los nodos **envían alertas** a la **Raspberry Pi** mediante **Bluetooth Low Energy (BLE)**.  
- La **Raspberry Pi** **procesa, almacena y gestiona** los eventos en la **Capa de Procesamiento**.  

---

## 🎯 **Nodos IoT ESP32 y su Función en la Red**  

El sistema cuenta con **cuatro nodos ESP32**, cada uno asignado a un conjunto de canales Wi-Fi para realizar la detección de ataques:  

| **Nodo IoT**       | **Función**  |
|--------------------|--------------|
| **ESP32_ch_01** 🎯 | Monitorea el **canal 1**. |
| **ESP32_ch_06** 🎯 | Monitorea el **canal 6**. |
| **ESP32_ch_11** 🎯 | Monitorea el **canal 11**. |
| **ESP32_ch_Scan** 🔄 | Escanea los canales **2-5, 7-10 y 12-13**. |

Cada **ESP32** captura los paquetes Wi-Fi en su canal y, si detecta un posible ataque de desautenticación, envía una alerta a la **Raspberry Pi** a través de **BLE**.

---

## 🖥 **Instalación en Raspberry Pi**  

### 1️⃣ **Instalar el sistema operativo**  

1. Descarga **Raspberry Pi OS (Debian 12 - Bookworm)** desde:  
   - 🔗 [Raspberry Pi OS](https://www.raspberrypi.com/software/)  
2. Instala la imagen en una tarjeta SD utilizando **Raspberry Pi Imager**.  
3. Configura **SSH y Wi-Fi** para acceso remoto (opcional).  

---

### 2️⃣ **Acceder a la Raspberry Pi por SSH**  

Para conectarte desde otra máquina, abre una terminal y ejecuta:

```bash
ssh pi@<IP_RASPBERRY_PI>
```

Ejemplo:

```bash
ssh pi@192.168.1.100
```

Si es la primera vez que te conectas, aparecerá un mensaje de autenticación. Escribe **`yes`** y presiona **Enter**.

---

### 3️⃣ **Actualizar e instalar dependencias**  

Ejecuta el siguiente comando para asegurarte de que el sistema esté **actualizado** y tenga las herramientas necesarias para el desarrollo:  

```bash
sudo apt update && sudo apt upgrade -y
```

- **`sudo apt update`**: Descarga la lista de paquetes más recientes disponibles en los repositorios.  
- **`sudo apt upgrade -y`**: Instala todas las actualizaciones disponibles para el sistema.  

Luego, instala los paquetes requeridos para el proyecto:

```bash
sudo apt install git python3 python3-pip python3-venv bluetooth bluez -y
```

🔹 **Explicación de los paquetes:**  
- **`git`** → Para clonar el repositorio del proyecto.  
- **`python3`** → Versión 3 de Python, necesaria para ejecutar el código.  
- **`python3-pip`** → Administrador de paquetes de Python.  
- **`python3-venv`** → Permite la creación de entornos virtuales en Python.  
- **`bluetooth` y `bluez`** → Controladores y herramientas para gestionar conexiones **BLE** en Raspberry Pi.  

---

### 4️⃣ **Clonar el repositorio y cambiar a la rama `processing-layer`**  

📌 **Ubica la carpeta donde deseas clonar el repositorio:**  

Si deseas organizar mejor tu sistema, puedes **crear una carpeta** para almacenar el proyecto, por ejemplo, `GitHub`:

```bash
cd ~
mkdir GitHub && cd GitHub
```

Luego, clona el repositorio y accede a la rama de processing-layer:

```bash
git clone git@github.com:Eberth-sys/Deauth-Alert-WiFi-IoT-System.git
cd Deauth-Alert-WiFi-IoT-System
git checkout processing-layer
```
---

### 5️⃣ **Crear y activar un entorno virtual**  

Para evitar conflictos con dependencias del sistema, se recomienda trabajar dentro de un **entorno virtual de Python**.  

📌 **Ubica primero la carpeta del proyecto:**  

```bash
cd ~/GitHub/Deauth-Alert-WiFi-IoT-System/processing-layer
```

Luego, crea el entorno virtual:

```bash
python3 -m venv ble
```

Actívalo con:

```bash
source ble/bin/activate
```

Deberías ver que el prompt de la terminal cambia a algo como:

```bash
(ble) pi@raspberrypi:~/GitHub/Deauth-Alert-WiFi-IoT-System/processing-layer $
```

---

### 6️⃣ **Instalar las dependencias**  

Ejecuta el siguiente comando dentro del entorno virtual **activo**:

```bash
pip install -r requirements.txt
```

---

## 🔧 **Detección de ESP32 mediante Bluetooth**  

Para comprobar que los **ESP32** están transmitiendo BLE, usa:

```bash
bluetoothctl
scan on
```

Ejemplo de salida esperada:

```
[NEW] Device AA:BB:CC:DD:EE:FF ESP32_1_CH_01
[NEW] Device 11:22:33:44:55:66 ESP32_2_CH_06
```

Si los dispositivos aparecen en la lista, están listos para la conexión.

---
### 🛠 **Solución de Problemas al Escanear Dispositivos con Bluetooth**  

Si el **Bluetooth** no detecta los **ESP32**, asegúrate de que:  
- Los **ESP32 están encendidos**.  
- El **código ha sido correctamente cargado en cada ESP32**.  

Si el problema persiste, puedes intentar reiniciar el servicio **Bluetooth** con los siguientes comandos:  

```bash
sudo systemctl restart bluetooth
bluetoothctl
scan on
```

Si experimentas **problemas de permisos**, agrega tu usuario al grupo de **Bluetooth** y reinicia la Raspberry Pi:  

```bash
sudo usermod -aG bluetooth pi
sudo reboot
```

---

## 🚀 **Ejecución del Proyecto**  

### 7️⃣ **Configurar `devices.yaml`**  

Para que el sistema pueda reconocer los nodos **ESP32**, es necesario definir sus direcciones **MAC** y los **UUIDs** del servicio BLE en un archivo de configuración.  

📌 **Primero, copia el archivo de ejemplo y renómbralo como `devices.yaml`**  

```bash
cp config/devices.yaml.example config/devices.yaml
```

📌 **Ahora edita el archivo `devices.yaml` para ingresar las direcciones MAC de los ESP32 detectados:**  

```bash
nano config/devices.yaml
```

📌 **Ejemplo de configuración:**  

```yaml
# ⚠️ IMPORTANTE: Reemplaza las direcciones MAC y UUIDs con los valores reales antes de ejecutar el sistema.

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
  # 🔑 UUID del servicio BLE (Debe coincidir con el configurado en los ESP32)
  service_uuid: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"  

  # 📡 UUID de la característica BLE utilizada para recibir datos
  characteristic_uuid: "yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy"
```

📌 **Guarda y cierra el archivo:**  
1. **Presiona `Ctrl + O`** y luego **Enter** para guardar los cambios.  
2. **Presiona `Ctrl + X`** para salir del editor Nano.  

---

### 8️⃣ **Ejecutar el script principal**  

```bash
python main.py
```
✅ **Salida esperada:**
```
[INFO] Buscando ESP32_1_CH_01...
[CONNECTED] Conectado a ESP32_1_CH_01
[INFO] Esperando datos de ESP32_1_CH_01...
```
---

## 👨‍💻 **Autor**  

<div style="display: flex; align-items: flex-start; background: #222; border-left: 5px solid #4da6ff; padding: 20px; border-radius: 10px; box-shadow: 3px 3px 15px rgba(0,0,0,0.3); font-family: Arial, sans-serif;">

  <div style="flex: 1; color: #ddd;">
    <h2 style="margin: 0; color: #4da6ff; display: flex; align-items: center;">
      Ing. Eberth Alarcón 
      <a href="https://www.linkedin.com/in/eberthalarcon90" target="_blank" style="margin-left: 10px; font-size: 16px; color: #4da6ff; text-decoration: none; display: flex; align-items: center;">
        <img src="https://upload.wikimedia.org/wikipedia/commons/c/ca/LinkedIn_logo_initials.png" alt="LinkedIn" width="20" style="margin-right: 5px;"> LinkedIn
      </a>
    </h2>
    <hr style="border: 0; height: 2px; background: #4da6ff; margin: 10px 0;">
    <p style="margin: 5px 0; font-size: 15px;"><strong>🏛️ Universidad de Buenos Aires (UBA) 🇦🇷</strong></p>
    <p style="margin: 5px 0; font-size: 15px;"><strong>📚 Facultad de Ingeniería</strong></p>
    <p style="margin: 5px 0; font-size: 15px;"><strong>📡 Especialización en Internet de las Cosas (IoT)</strong></p>
  </div>

  <div style="flex: 0 0 180px; text-align: right; margin-top: 60px;">
    <img src="https://i.postimg.cc/nz9jwWQG/uba-logo.png" alt="Universidad de Buenos Aires" width="180" style="border-radius: 5px; background: #fff; padding: 5px;">
  </div>

</div>


