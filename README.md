
# Sistema IoT para el monitoreo y detección de ataques de desautenticación en redes Wi-Fi<!-- omit in toc -->

## Índice <!-- omit in toc -->

<!-- TOC levels="2..4" -->

- [Descripción general](#descripción-general)
  - [Propósito y beneficios](#propósito-y-beneficios)
  - [Estado Del Arte](#estado-del-arte)
  - [Investigación y desarrollo](#investigación-y-desarrollo)
- [Estructura del proyecto](#estructura-del-proyecto)
  - [Backend](#backend)
  - [Frontend](#frontend)
  - [Processing layer](#processing-layer)
- [Instrucciones De Instalación](#instrucciones-de-instalación)
  - [Requisitos](#requisitos)
  - [Pasos para ejecutar el proyecto](#pasos-para-ejecutar-el-proyecto)
- [Contribuciones](#contribuciones)
- [Acerca del autor.](#acerca-del-autor)
- [📄 Licencia](#-licencia)


## Descripción general

El **Sistema IoT para el Monitoreo y Detección de Ataques de Desautenticación en Redes Wi-Fi** es una solución innovadora desarrollada con el objetivo de incrementar la seguridad en redes inalámbricas mediante la detección temprana de ataques de desautenticación. Este sistema, diseñado especialmente para entornos empresariales, utiliza una infraestructura de **Internet de las Cosas (IoT)** para analizar en tiempo real el tráfico de redes Wi-Fi y emitir alertas cuando se detectan comportamientos anómalos asociados a intentos de desconexión forzada.

### Propósito y beneficios

La principal motivación detrás de este proyecto es fortalecer la protección de redes Wi-Fi ante la amenaza de los ataques de desautenticación, un tipo de **Denial of Service (DoS)** que puede comprometer la disponibilidad de la red y permitir ataques más complejos, como la suplantación de puntos de acceso (Evil Twin). El sistema propuesto tiene como objetivo mejorar la seguridad operativa, ofreciendo:

* **Monitoreo en tiempo real**: análisis continuo del tráfico de red para identificar intentos de ataque.
* **Detección temprana**: generación de alertas inmediatas para facilitar la intervención rápida y la mitigación de amenazas.
* **Bajo costo y alta escalabilidad**: implementación eficiente con dispositivos de bajo costo, lo que permite su adopción en empresas de cualquier tamaño sin requerir infraestructuras avanzadas ni personal altamente especializado.
* **Integración sencilla**: la solución puede ser implementada en redes existentes sin necesidad de modificaciones complejas.

### Estado Del Arte

El campo de la seguridad en redes Wi-Fi ha sido objeto de diversas investigaciones a lo largo de los años. Sin embargo, muchos de los métodos actuales de protección contra ataques de desautenticación requieren de infraestructuras complejas, lo que limita su accesibilidad para pequeñas y medianas empresas. Las soluciones tradicionales como **Aircrack-ng** y **Wireshark**, si bien eficaces para el análisis del tráfico, requieren de supervisión constante y no proporcionan una respuesta automatizada ante incidentes.

Por otro lado, sistemas más avanzados como **WIDS/IPS** (Sistemas de Detección de Intrusos en Redes Inalámbricas) ofrecen soluciones robustas, pero su implementación es costosa y difícil de adaptar a redes convencionales. En este contexto, el sistema propuesto utiliza tecnologías de bajo costo como el **ESP32** y el **Bluetooth Low Energy (BLE)** para proporcionar una solución escalable, autónoma y de fácil integración.

### Investigación y desarrollo

La investigación realizada se centró en el estudio de los protocolos Wi-Fi, los ataques de desautenticación y las soluciones IoT aplicables a la seguridad de redes. Se investigaron enfoques previos, y se identificaron las limitaciones de las tecnologías existentes. A partir de allí, se diseñó y desarrolló un sistema capaz de detectar en tiempo real los ataques de desautenticación utilizando dispositivos ESP32 configurados en modo promiscuo para la captura de tráfico en redes Wi-Fi de 2,4 GHz.

El desarrollo incluyó:

* **Diseño del hardware**: configuración de los nodos sensores ESP32 para capturar paquetes de gestión de redes Wi-Fi.
* **Desarrollo del software**: programación del firmware en C/C++ para los ESP32 y la creación del backend con **FastAPI** para el procesamiento de los eventos detectados.
* **Implementación de la base de datos**: uso de **PostgreSQL** para almacenar los eventos y los estados de los nodos sensores.
* **Desarrollo de la interfaz gráfica**: implementación de una interfaz web con **React** y **TailwindCSS** para la visualización en tiempo real de las alertas.

## Estructura del proyecto

La estructura de este proyecto está organizada en varios módulos, cada uno con su propio propósito y responsabilidad. A continuación se describe brevemente la organización general:

```
DEAUTH-ALERT-WIFI-IOT-SYSTEM/
├── .vscode/                 # Configuraciones de entorno para Visual Studio Code (como debug o extensiones).
├── backend/                 # Carpeta principal del backend del sistema (API, base de datos, lógica del servidor).
├── frontend/                # Carpeta principal del frontend (interfaz web con React + TypeScript).
├── node_modules/            # Carpeta autogenerada con las dependencias instaladas por npm o yarn.
├── perception-layer/        # Capa de percepción con nodos ESP32 (código Arduino o ESP-IDF).
├── processing-layer/        # Capa de procesamiento, generalmente para análisis de datos o coordinación del sistema.
├── .env                     # Variables de entorno (configuraciones sensibles que no deben compartirse).
├── .env.example             # Plantilla de archivo `.env` para facilitar la configuración inicial.
├── .gitignore               # Define qué archivos o carpetas deben ser ignoradas por Git.
├── package-lock.json        # Registro exacto de las versiones de dependencias instaladas (autogenerado).
├── package.json             # Archivo principal de configuración del proyecto Node.js (scripts, dependencias, etc.).
└── README.md                # Documento de presentación o guía general del sistema completo.

```

### Backend

El backend está desarrollado con **FastAPI** y se encarga de gestionar los eventos capturados por los nodos ESP32, almacenarlos en una base de datos **PostgreSQL** y exponer los datos a través de un API. La gestión de usuarios, autenticación y las alertas en tiempo real son parte de las funcionalidades ofrecidas.

### Frontend

El frontend está desarrollado utilizando **React** con **Vite** y **TypeScript**, y permite a los usuarios interactuar con el sistema mediante una interfaz gráfica en tiempo real. Esta interfaz muestra las alertas, los reportes generados, y el estado de los nodos sensores.

### Processing layer

La capa de procesamiento se encarga de la comunicación con los nodos **ESP32** mediante **Bluetooth Low Energy (BLE)** y procesa los eventos de desautenticación para generar alertas en tiempo real. Además, esta capa gestiona la conexión con la base de datos y asegura la integridad y persistencia de los datos.

## Instrucciones De Instalación

### Requisitos

* **Raspberry Pi** con Raspbian OS.
* **ESP32** configurados con el firmware del sistema.
* **Docker** para la implementación del backend y la base de datos.
* **Python 3.8+** y **Node.js** para ejecutar el sistema.

### Pasos para ejecutar el proyecto

1. **Configurar el entorno local:**

   * Clona el repositorio y navega a la carpeta del proyecto.
   * Crea un archivo `.env` a partir de `.env.example` y configura las variables de entorno con los valores adecuados.

2. **Explora la estructura del proyecto:**
   En cada capa del proyecto (Frontend, Backend, Processing Layer, y los nodos ESP32) encontrarás un archivo **README** que explica en detalle cómo ejecutar y configurar cada proceso. Te invito a que indagues en cada una de estas carpetas para conocer las instrucciones específicas y asegurarte de que todo funcione de manera adecuada. Estos archivos README te guiarán paso a paso a través de la instalación, configuración y ejecución de cada parte del sistema, adaptadas a las necesidades de cada capa.

3. **Instalar dependencias del frontend:**

   ```bash
   cd frontend
   npm install
   ```

4. **Ejecutar el backend y la base de datos con Docker:**

   ```bash
   cd processing-layer/docker
   docker-compose up --build
   ```

5. **Iniciar el servidor frontend:**

   ```bash
   cd frontend
   npm start
   ```

6. **Acceder a la interfaz web:**

   * Visita `http://localhost:3000` para visualizar el estado del sistema y las alertas.

## Contribuciones

Las contribuciones a este proyecto son bienvenidas. Si deseas colaborar, por favor sigue los siguientes pasos:

1. Haz un fork del proyecto.
2. Crea una nueva rama para tu funcionalidad o corrección de errores (`git checkout -b feature/nueva-funcionalidad`).
3. Realiza tus cambios y haz commits (`git commit -am 'Agrega nueva funcionalidad'`).
4. Realiza un push a tu rama (`git push origin feature/nueva-funcionalidad`).
5. Crea un pull request detallando las modificaciones realizadas.

## Acerca del autor.

Soy **Eberth Gabriel Alarcón**, ingeniero electrónico especializado en telecomunicaciones, redes y ciberseguridad, con más de diez años de experiencia en el área de `TI`. He liderado e implementado soluciones de seguridad informática y redes, con un enfoque particular en tecnologías IoT. Este trabajo de grado representa una manifestación de mi compromiso con la innovación en el ámbito de la seguridad en redes, orientado a ofrecer soluciones prácticas y accesibles para proteger la infraestructura inalámbrica de pequeñas, medianas y grandes empresas. Actualmente, complemento mi perfil con estudios en `inteligencia artificial` y `machine learning`, con el propósito de integrar técnicas avanzadas de análisis y detección de amenazas en las soluciones que diseño para el ámbito de la ciberseguridad.

**Esp. Ing. Eberth Alarcón**  
🌐 [LinkedIn - Eberth Alarcón](https://www.linkedin.com/in/eberthalarcon90)  

**Universidad de Buenos Aires (UBA)** 🇦🇷  
**Facultad de Ingeniería**  -  **Especialización en Internet de las Cosas (IoT)**

<img src="https://i.postimg.cc/nz9jwWQG/uba-logo.png" alt="Universidad de Buenos Aires" width="300"/>

---

## 📄 Licencia

Proyecto bajo **Licencia MIT** (ver `LICENSE.md`).

---