# 🚀 Servicio Backend | Deauth‑Alert Wi‑Fi IoT System<!-- omit in toc -->

## 🗂️ Índice <!-- omit in toc -->

<!-- TOC levels="2..4" -->

- [🖥️ Descripción](#️-descripción)
- [📂 Estructura del backend](#-estructura-del-backend)
- [⚙️ Configuración del entorno](#️-configuración-del-entorno)
  - [📋 Requisitos previos](#-requisitos-previos)
- [🔧 Instalación y arranque](#-instalación-y-arranque)
- [🔗 Endpoints REST \& WebSocket](#-endpoints-rest--websocket)
  - [📡 REST API](#-rest-api)
  - [🌐 WebSocket](#-websocket)
- [🗄️ Modelos y esquemas](#️-modelos-y-esquemas)
- [💾 Base de datos](#-base-de-datos)
- [👨‍💻 **Autor**](#-autor)
- [📄 Licencia](#-licencia)

## 🖥️ Descripción

El **servicio backend** de este sistema proporciona una API desarrollada con **FastAPI** y una base de datos **PostgreSQL**. Sus objetivos principales son:

1. **Registrar** y almacenar alertas de desautenticación capturadas por nodos ESP32.
2. **Exponer** los datos mediante **endpoints REST** y **canal WebSocket** para comunicación en tiempo real.
3. **Gestionar** el estado de los dispositivos y **asegurar** la autenticación de usuarios.

A lo largo de este documento se detallan la instalación, configuración, uso y arquitectura de todos los componentes.

## 📂 Estructura del backend

```plaintext
DEAUTH-ALERT-WIFI-IOT-SYSTEM/           # Raíz del repositorio general
└── backend/                            # Carpeta del servicio backend
    ├── src/                           # Código fuente principal
    │   ├── __pycache__/               # Archivos compilados de Python
    │   ├── routes/                    # Definición de rutas HTTP y WebSocket
    │   │   ├── admin_routes.py        # Gestión de usuarios y permisos
    │   │   ├── alerts_summary.py      # Consultas agregadas de alertas
    │   │   ├── alerts.py              # Endpoints para alertas
    │   │   ├── auth.py                # Autenticación y autorización
    │   │   ├── custom_queries.py      # Consultas SQL personalizadas
    │   │   ├── esp32_nodes.py         # Estado y actualización de nodos ESP32
    │   │   ├── logs.py                # Lectura y descarga de logs
    │   │   └── websocket.py           # Canal WebSocket en tiempo real
    │   ├── services/                  # Lógica de negocio adicional
    │   │   └── auth_service.py        # Servicio de autenticación
    │   ├── tests/                     # Pruebas unitarias e integración
    │   ├── database.py                # Configuración de la base de datos y sesiones
    │   ├── main.py                    # Inicialización de la app y registro de routers
    │   ├── models.py                  # Definición de modelos ORM (SQLAlchemy)
    │   ├── requirements.txt           # Dependencias del proyecto
    │   └── schemas.py                 # Esquemas Pydantic para validación
    ├── .env                           # Variables de entorno (no versionar)
    ├── .env.example                   # Plantilla de variables de entorno
    └── README.md                      # Documentación principal del backend

```

## ⚙️ Configuración del entorno

### 📋 Requisitos previos

* **Python 3.8 o superior**
* **Git**
* **PostgreSQL** en ejecución
* **Docker & Docker Compose** (opcional para base de datos)
* **Virtualenv** o similar (recomendado)

## 🔧 Instalación y arranque

1. **Clonar el repositorio y entrar en el backend**:

   ```bash
   git clone https://github.com/usuario/DEAUTH-ALERT-WIFI-IOT-SYSTEM.git
   cd DEAUTH-ALERT-WIFI-IOT-SYSTEM/backend
   ```

2. **Crear y activar un entorno virtual**:

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Linux/macOS
   .venv\Scripts\activate       # Windows
   ```

3. **Instalar dependencias**:

   ```bash
   pip install --upgrade pip
   pip install -r src/requirements.txt
   ```

4. **Configurar la base de datos**:

   1. Copiar la plantilla de entorno:

      ```bash
      cp .env.example .env
      ```
   2. Abrir `.env` y completar las variables:

      * `PG_DB`: nombre de la base de datos
      * `PG_USER`: usuario de PostgreSQL
      * `PG_PASSWORD`: contraseña del usuario
      * `PG_HOST`: dirección del servidor de DB
      * `PG_PORT`: puerto de conexión
   3. Ver sección **Plantilla de archivo `.env`** para más detalles sobre cada variable.
      1.  Abrir el archivo .env recién creado.
   
   Reemplazar cada valor de variable por sus credenciales y rutas correspondientes:
   
   Guardar los cambios y verificar que el archivo .env esté excluido del control de versiones.

    ```bash

    # ==========================================================================================================
    # 📦 Archivo de ejemplo .env para la configuración del sistema IoT
    # 🛠️ Este archivo contiene las variables necesarias para ejecutar el backend del proyecto.
    # ==========================================================================================================

    # -------------------- 🗄️ Configuración de la base de datos PostgreSQL --------------------
    PG_DB=deauth_alerts           # Nombre de la base de datos creada en PostgreSQL
    PG_USER=your_username         # Usuario con permisos de lectura/escritura
    PG_PASSWORD=your_secure_password  # Contraseña del usuario de la base de datos
    PG_HOST=localhost             # Dirección del servidor de la base de datos
    PG_PORT=5432                  # Puerto de conexión (por defecto: 5432)

    # 🔗 URL de conexión completa para SQLAlchemy
    # Construida automáticamente con las variables anteriores.
    DATABASE_URL=postgresql://$PG_USER:$PG_PASSWORD@$PG_HOST:$PG_PORT/$PG_DB

    # -------------------- 🔐 Configuración de autenticación JWT --------------------
    JWT_SECRET_KEY=replace_with_a_long_random_string  # Clave secreta para firmar los tokens JWT
    JWT_ALGORITHM=HS256                              # Algoritmo de firma (p.ej.: HS256)
    JWT_EXPIRE_MINUTES=1440                           # Duración del token en minutos (1440 = 24 h)

    # -------------------- 🤖 Configuración de notificaciones por Telegram --------------------
    TELEGRAM_BOT_TOKEN=your_telegram_bot_token        # Token del bot creado en Telegram via BotFather
    TELEGRAM_CHAT_ID=your_telegram_chat_id            # ID del chat o grupo que recibirá las alertas

    # -------------------- 🌐 Control de orígenes permitidos (CORS) --------------------
    # Enumerar las URLs desde las que el frontend podrá hacer peticiones
    CORS_ORIGINS=http://localhost:5173,http://192.168.0.100:5173

    # -------------------- 📝 Ruta para almacenamiento de logs --------------------
    LOGS_DIR=/ruta/a/tu/repositorio/processing-layer/logs  # Carpeta donde se guardan los archivos de registro

    # -------------------- 🔗 URL del frontend --------------------
    # Usada para redirecciones y generación de enlaces en correos
    FRONTEND_URL=http://localhost:5173
    ```

    ⚠️  Consejo: Mantenga este archivo fuera del control de versiones (.gitignore) y gestione sus credenciales con cuidado.



1. **Arrancar el servidor**:
   
   Ejecute el siguiente comando para arrancar la aplicación con recarga automática:

   ```bash
   `uvicorn src.main:app --reload --host $HOST --port $PORT`
   ```
    ⚠️ Reemplace `$HOST` y `$PORT` por los valores definidos en el archivo .env.

2. **Ver documentación interactiva**:
   
   Abra en navegador:

   ```bash
   http://$HOST:$PORT/docs
   ````
    Esta interfaz de Swagger UI permite explorar y probar todos los endpoints disponibles.


## 🔗 Endpoints REST & WebSocket

### 📡 REST API

| Método | Ruta                        | Descripción                                                  |
| ------ | --------------------------- | ------------------------------------------------------------ |
| GET    | `/alerts`                   | Recupera las últimas N alertas (parámetro opcional `limit`). |
| POST   | `/alerts`                   | Crea una nueva alerta.                                       |
| GET    | `/alerts-summary`           | Obtiene estadísticas agregadas por canal y último timestamp. |
| GET    | `/esp32-nodes`              | Lista el estado de todos los nodos ESP32.                    |
| POST   | `/esp32-nodes/update`       | Actualiza el estado de un nodo y emite WebSocket.            |
| GET    | `/logs`                     | Lista archivos de registro.                                  |
| GET    | `/logs/{filename}`          | Devuelve el contenido del log línea a línea.                 |
| GET    | `/logs/download/{filename}` | Descarga el archivo de log completo.                         |

### 🌐 WebSocket

* **URL:** `ws://$HOST:$PORT/ws/alerts`
* **Función:** Emite en tiempo real todas las nuevas alertas y cambios de estado de nodos.

## 🗄️ Modelos y esquemas

| Archivo      | Motor      | Clases / Schemas                                  | Descripción                                                                  |
| ------------ | ---------- | ------------------------------------------------- | ---------------------------------------------------------------------------- |
| `models.py`  | SQLAlchemy | `Alert``ESP32Status`                              | Define las tablas: `alerts` y `esp32_status` con sus campos y restricciones. |
| `schemas.py` | Pydantic   | `AlertCreate``AlertResponse``ESP32StatusResponse` | Valida y serializa datos en peticiones y respuestas.                         |

## 💾 Base de datos

Se utiliza **PostgreSQL**. Las tablas se generan automáticamente al iniciar la aplicación:

| Tabla          | Descripción                                                 |
| -------------- | ----------------------------------------------------------- |
| `alerts`       | Registra eventos de desautenticación (BSSID, canal, fecha). |
| `esp32_status` | Guarda estado (`connected`/`disconnected`) de cada nodo.    |

## 👨‍💻 **Autor**

**Esp. Ing. Eberth Alarcón**  
🌐 [LinkedIn - Eberth Alarcón](https://www.linkedin.com/in/eberthalarcon90)  

**Universidad de Buenos Aires (UBA)** 🇦🇷  
**Facultad de Ingeniería**  -  **Especialización en Internet de las Cosas (IoT)**

<img src="https://i.postimg.cc/nz9jwWQG/uba-logo.png" alt="Universidad de Buenos Aires" width="300"/>

---

## 📄 Licencia

Licencia **pendiente de definición** — se establecerá antes de la publicación pública. Hasta entonces, © 2025 Eberth Alarcón, todos los derechos reservados.

---