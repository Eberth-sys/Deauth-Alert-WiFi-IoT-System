<p align="center">
  <img src="docs/img/banner.svg" alt="Deauth-Alert, detección en tiempo real de ataques de desautenticación Wi-Fi 802.11" width="100%">
</p>

<p align="center">
  <i>Sistema IoT para el monitoreo y detección de ataques de desautenticación en redes Wi-Fi</i>
</p>

<p align="center">
  <img alt="Estado" src="https://img.shields.io/badge/estado-prototipo%20de%20tesis-1e293b">
  <img alt="Licencia" src="https://img.shields.io/badge/licencia-Apache%202.0-blue">
  <img alt="ESP32" src="https://img.shields.io/badge/ESP32-WROOM--32U-E7352C?logo=espressif&logoColor=white">
  <img alt="Raspberry Pi" src="https://img.shields.io/badge/Raspberry%20Pi-OS-A22846?logo=raspberrypi&logoColor=white">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white">
  <img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-0.139-009688?logo=fastapi&logoColor=white">
  <img alt="React" src="https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black">
  <img alt="PostgreSQL" src="https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white">
  <img alt="Docker" src="https://img.shields.io/badge/Docker-compose-2496ED?logo=docker&logoColor=white">
</p>

<p align="center">
  <b>Vigilancia distribuida del espectro Wi-Fi de 2,4 GHz con nodos ESP32, Raspberry Pi, alertas en tiempo real y panel web.</b>
</p>

<p align="center">
  <a href="https://youtu.be/P1Kr70pG77Y"><b>▶️ Ver demostración</b></a>
  &nbsp;·&nbsp;
  <a href="https://www.youtube.com/watch?v=JqII7Z1xTyE">🎓 Defensa de tesis (UBA)</a>
  &nbsp;·&nbsp;
  <a href="https://lse-posgrados-files.fi.uba.ar/tesis/LSE-FIUBA-Trabajo-Final-CEIoT-Eberth-Gabriel-Alarcon-Gonzalez-2025.pdf">📄 Tesis (PDF)</a>
</p>

> **Trabajo de tesis** · Especialización en Internet de las Cosas (IoT) · Facultad de Ingeniería · Universidad de Buenos Aires (UBA).

---

## En resumen

> **Los ataques de desautenticación suelen ocurrir sin visibilidad real para quien administra y protege una red. Deauth-Alert fue creado para resolver este problema.**
>
> En muchos entornos Wi-Fi, estos eventos no se detectan a tiempo, no quedan registrados de forma estructurada y solo se evidencian cuando la desconexión ya afecta la operación. Este trabajo convierte ese punto ciego en una señal visible, registrable y accionable.
>
> Para quien administra y protege una red, esto significa mayor capacidad de monitoreo y respuesta. Para quien intenta vulnerarla, significa una menor posibilidad de actuar sin dejar evidencia.
>
> **Tres pilares de Deauth-Alert:**<br>📡 **Detectar** · 🗂️ **Registrar** · 🔔 **Alertar**

---

| ⚠️ **Uso responsable y autorizado** |
| :--- |
| Este sistema configura interfaces Wi-Fi en modo promiscuo para detectar ataques de desautenticación 802.11. Úselo únicamente en redes propias o con autorización explícita. La captura de tráfico de terceros puede infringir la legislación aplicable. El autor no se responsabiliza por usos indebidos. |

---

## Índice

- [Descripción general](#descripción-general)
- [Arquitectura](#arquitectura)
- [Tecnologías](#tecnologías)
- [Estructura del repositorio](#estructura-del-repositorio)
- [Puesta en marcha](#puesta-en-marcha)
- [Evidencia académica y recursos públicos](#evidencia-académica-y-recursos-públicos)
- [Estado del proyecto](#estado-del-proyecto)
- [Alcance actual](#alcance-actual)
- [Próximas mejoras](#próximas-mejoras)
- [Apoye el proyecto](#apoye-el-proyecto)
- [Sobre el autor](#sobre-el-autor)
- [Licencia](#licencia)

---

## Descripción general

Sistema IoT distribuido que detecta en tiempo real ataques de desautenticación 802.11, un tipo de denegación de servicio (DoS) que fuerza la desconexión de clientes Wi-Fi y habilita ataques más complejos, como la suplantación de puntos de acceso (*Evil Twin*).

**Objetivos:**

- Monitoreo en tiempo real del tráfico de gestión Wi-Fi en 2,4 GHz.
- Detección temprana con alertas inmediatas (panel web, Telegram y nube).
- Bajo costo y escalabilidad con hardware accesible (ESP32 + Raspberry Pi).

**Contexto (estado del arte):** herramientas como *Aircrack-ng* o *Wireshark* resultan eficaces para el análisis, pero requieren supervisión continua y no automatizan la respuesta; las soluciones comerciales de detección de intrusiones (*WIDS/IPS*) son robustas, aunque costosas y difíciles de adaptar. Este proyecto explora una alternativa autónoma y de bajo costo basada en el ESP32-WROOM-32U en modo promiscuo y *Bluetooth Low Energy* (BLE).

---

## Arquitectura

El sistema se organiza en cuatro capas, desde la captura del ataque hasta la visualización en tiempo real.

![Arquitectura del sistema](docs/img/architecture.svg)

**Flujo de un evento (detección → alerta):**

1. Un nodo ESP32 en modo promiscuo captura una *trama* de desautenticación 802.11.
2. El nodo compara el BSSID objetivo y, ante una coincidencia, emite una alerta por BLE.
3. La Raspberry Pi recibe la alerta, la persiste en PostgreSQL y la publica a AWS IoT y Telegram.
4. El backend FastAPI expone la alerta por REST y la difunde por WebSocket.
5. El panel React muestra la alerta en tiempo real.

![Flujo de un evento](docs/img/event-flow.svg)

![Panel de capas del sistema](docs/img/layers.svg)

---

## Tecnologías

| Capa | Manual técnico | Tecnología | Rol |
| --- | --- | --- | --- |
| Percepción | [Arduino](perception-layer/esp32-nodes-ino/README.md) · [ESP-IDF](perception-layer/espidf-nodes/README.md) | ESP32-WROOM-32U · C/C++ (Arduino `.ino` y ESP-IDF `.c`) | Captura de *tramas* de desautenticación en modo promiscuo; envío por BLE |
| Procesamiento | [Procesamiento](processing-layer/README.md) | Python (`bleak`, `paho-mqtt`, `psycopg2`) · Docker/PostgreSQL | Ingesta BLE, persistencia, publicación MQTT/AWS IoT y Telegram |
| Backend | [Backend](backend/README.md) | FastAPI · SQLAlchemy · PostgreSQL · JWT | API REST + WebSocket + autenticación |
| Frontend | [Frontend](frontend/README.md) | React · Vite · TypeScript · TailwindCSS | Panel en tiempo real |

**Versiones principales** (tomadas de `requirements.txt`, `package.json`, los Dockerfiles y `docker-compose.yml`):

| Componente | Versión |
| --- | --- |
| Python | 3.11 |
| FastAPI · Uvicorn | 0.139 · 0.51 |
| SQLAlchemy · Pydantic | 2.0 · 2.13 |
| PostgreSQL | 16 |
| React · Vite · TypeScript | 19 · 6 · 5.7 |
| Node (compilación) · nginx | 22 · 1.31 |

> Cada manual técnico detalla la instalación y configuración de su capa.

---

## Estructura del repositorio

```
Deauth-Alert-WiFi-IoT-System/
├── perception-layer/     # Firmware ESP32 (Arduino .ino + ESP-IDF .c), modo promiscuo
├── processing-layer/     # Raspberry Pi: ingesta BLE, PostgreSQL (Docker), MQTT/AWS, Telegram
├── backend/              # API FastAPI + PostgreSQL + JWT + WebSocket (Dockerfile incluido)
├── frontend/             # Panel React + Vite + TypeScript (Dockerfile + nginx.conf)
├── docs/img/             # Diagramas y banner (SVG) usados en la documentación
├── docker-compose.yml    # Conjunto de servicios web: postgres + backend + frontend (docker compose up)
├── .env.example          # Plantilla de variables de entorno (los .env reales NO se versionan)
├── .gitignore
└── README.md
```

> Los archivos sensibles (`.env`, certificados, `config.h` de los nodos) **no se versionan**; se proveen plantillas `.example` / `_template`.

---

## Puesta en marcha

**Requisitos:** Docker (para el conjunto de servicios web). Para el laboratorio físico, además: Raspberry Pi (Raspberry Pi OS) · 4× ESP32-WROOM-32U · Python 3.11+ · Node.js 20+.

```bash
git clone https://github.com/Eberth-sys/Deauth-Alert-WiFi-IoT-System.git
cd Deauth-Alert-WiFi-IoT-System
```

### Opción A. Conjunto de servicios web con Docker (recomendada, sin hardware)

Levanta **postgres + backend + frontend** con un solo comando (configuración por variables de entorno; los secretos provienen del `.env` en **tiempo de ejecución**, nunca incrustados en las imágenes):

```bash
cp .env.example .env          # completar: PG_*, JWT_SECRET_KEY (>=32), SERVICE_API_KEY, CORS_ORIGINS, VITE_*
docker compose up --build
```

| Servicio | URL |
| --- | --- |
| Frontend (panel) | http://localhost:8080 |
| Backend (API + `/docs`) | http://localhost:8000 |
| PostgreSQL | localhost:5432 |

> La capa `processing-layer` (BLE) y el firmware ESP32 **no** están en este `docker compose`: requieren hardware (Raspberry Pi + nodos ESP32) y se ejecutan aparte (ver Opción B y el laboratorio).

### Opción B. Ejecución manual y desarrollo por capa

> El detalle completo de cada capa está en su `README.md`. Comandos por capa:

**1. Base de datos (PostgreSQL en Docker · solo capa de borde/RPi)**
```bash
cd processing-layer/docker
cp .env.example .env          # completar credenciales
docker compose up -d          # este compose (borde/RPi) levanta SOLO PostgreSQL; conjunto de servicios web completo: Opción A
```

**2. Backend (FastAPI),** con `uvicorn` (o dentro de un contenedor mediante la Opción A):
```bash
cd backend/src
cp .env.example .env
pip install -r requirements.txt
uvicorn main:app --reload     # http://localhost:8000 · documentación: /docs
```

**3. Frontend (React + Vite)**
```bash
cd frontend
cp .env.example .env
npm install
npm run dev                   # http://localhost:5173
```

**4. Capa de procesamiento (Raspberry Pi, BLE)**
```bash
cd processing-layer
cp config/devices.yaml.example config/devices.yaml   # MAC/UUID de los nodos
pip install -r requirements.txt
python main.py                # requiere Bluetooth (BlueZ) y los ESP32 emparejados
```

**5. Firmware ESP32.** Ver [`perception-layer/`](perception-layer/) para compilar y grabar los nodos (crear `config.h` a partir de la plantilla).

---

## Evidencia académica y recursos públicos

- 📄 **Trabajo Final (tesis, PDF):** [LSE-FIUBA · CEIoT · 2025](https://lse-posgrados-files.fi.uba.ar/tesis/LSE-FIUBA-Trabajo-Final-CEIoT-Eberth-Gabriel-Alarcon-Gonzalez-2025.pdf)
- 📊 **Presentación de la tesis (PDF):** [diapositivas de la defensa](https://lse-posgrados-files.fi.uba.ar/tesis/LSE-FIUBA-Trabajo-Final-CEIoT-Eberth-Gabriel-Alarcon-Gonzalez-2025-Presentacion.pdf)
- 🎓 **Defensa de la tesis (UBA, video):** [ver en YouTube](https://www.youtube.com/watch?v=JqII7Z1xTyE)
- ▶️ **Demostración del sistema (video):** [ver en YouTube](https://youtu.be/P1Kr70pG77Y)

### Cómo citar

```bibtex
@thesis{alarcon2025deauthalert,
  author = {Alarcón González, Eberth Gabriel},
  title  = {Sistema IoT para el monitoreo y detección de ataques de desautenticación en redes Wi-Fi},
  school = {Universidad de Buenos Aires, Facultad de Ingeniería},
  year   = {2025},
  type   = {Trabajo Final de la Carrera de Especialización en Internet de las Cosas}
}
```

---

## Estado del proyecto

Deauth-Alert se diseñó desde el inicio con una arquitectura orientada a producción: autenticación JWT, configuración por variables de entorno, contenedores Docker reproducibles y separación por capas (percepción, procesamiento, backend, frontend). Hoy es un **prototipo académico funcional**, validado en laboratorio con nodos ESP32 y una Raspberry Pi. Las consideraciones de seguridad y despliegue para avanzar hacia un entorno productivo se documentan en [`SECURITY.md`](SECURITY.md).

---

## Alcance actual

- Detección en tiempo real de ataques de desautenticación 802.11 en la banda de 2,4 GHz.
- Alertas por panel web, Telegram y nube (AWS IoT).
- Despliegue reproducible de PostgreSQL, backend y frontend mediante Docker (`docker compose up`).
- La capa de percepción (firmware ESP32) y la capa de procesamiento (BLE, Raspberry Pi) operan sobre hardware dedicado.

---

## Próximas mejoras

- Contrato ESP32 → Raspberry Pi en formato JSON versionado.
- Contenerización de la capa de borde y compilación con ESP-IDF.
- Ampliación de la cobertura de pruebas.
- *(Exploratorio)* Incorporación de IA y aprendizaje automático para la correlación de eventos y la detección de anomalías.

---

## Apoye el proyecto

Si este trabajo le resulta útil, puede colaborar de varias formas:

- ⭐ Marque el repositorio con una **estrella** para darle visibilidad.
- 🐛 Informe errores o sugerencias mediante **incidencias**.
- 🔧 Proponga mejoras a través de **solicitudes de incorporación**.
- 📢 Comparta el enlace del proyecto con comunidades académicas, técnicas y de investigación.

> El uso, modificación y distribución del código y de la documentación propia se rigen por la licencia Apache 2.0.

---

## Sobre el autor

**Esp. Ing. Eberth Gabriel Alarcón González**
Ingeniero Electrónico, mención Telecomunicaciones · Especialista en Internet de las Cosas

### 👤 Perfil profesional

Ingeniero Electrónico con mención en Telecomunicaciones (URBE, 2014) y especialista en Internet de las Cosas (Universidad de Buenos Aires). Más de diez años de trayectoria en tecnologías de la información, con base en telecomunicaciones, redes e infraestructura, y los últimos años con foco en ciberseguridad.

Actualmente trabaja como ingeniero de ciberseguridad. Su foco combina la seguridad de sistemas de inteligencia artificial y modelos de lenguaje (IA y LLM), la seguridad de IoT, las pruebas de penetración, la seguridad de redes y la respuesta a incidentes. Deauth-Alert es el Trabajo Final de su especialización en IoT y refleja ese cruce entre redes, dispositivos conectados y seguridad.

### 🎓 Formación académica

- **Especialización en Internet de las Cosas** · Universidad de Buenos Aires, Argentina (2025). Deauth-Alert corresponde al Trabajo Final de esta carrera.
- **Ingeniería Electrónica, mención Telecomunicaciones** · Universidad Rafael Belloso Chacín, Venezuela (2014).

### 🛡️ Áreas de especialidad

- Ciberseguridad y respuesta a incidentes.
- Seguridad de sistemas de IA y modelos de lenguaje (IA y LLM).
- Seguridad de dispositivos y arquitecturas IoT.
- Pruebas de penetración y evaluación de vulnerabilidades.
- Seguridad de redes y endpoints.
- Telecomunicaciones e infraestructura de redes.

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Eberth%20Alarcón%20González-0A66C2?logo=linkedin&logoColor=white)](https://www.linkedin.com/in/eberthalarcon90)

<img src="docs/img/logo-uba.png" alt="Facultad de Ingeniería de la Universidad de Buenos Aires" width="200">

Facultad de Ingeniería (FIUBA), Universidad de Buenos Aires · Carrera de Especialización en Internet de las Cosas

---

## Licencia

El código y la documentación propia de este repositorio se distribuyen bajo la licencia Apache 2.0. Consulte [LICENSE](LICENSE) para los términos de uso y [NOTICE](NOTICE) para la atribución, marcas y materiales excluidos.

© 2025-2026 Esp. Ing. Eberth Gabriel Alarcón González.

---
