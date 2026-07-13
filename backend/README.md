> 🌐 **[English](README.en.md)** · **Español**

# Backend

⬅ Parte de [Deauth-Alert](../README.md)

<p align="left">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white">
  <img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-0.139-009688?logo=fastapi&logoColor=white">
  <img alt="PostgreSQL" src="https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white">
  <img alt="JWT" src="https://img.shields.io/badge/Auth-JWT-000000?logo=jsonwebtokens&logoColor=white">
  <img alt="Licencia" src="https://img.shields.io/badge/licencia-Apache%202.0-blue">
</p>

Manual técnico del backend: API REST y WebSocket desarrollados con FastAPI sobre PostgreSQL. Registra alertas de desautenticación, gestiona el estado de los nodos ESP32 y autentica usuarios y servicios.

## Índice

- [Descripción](#descripción)
- [Estructura del backend](#estructura-del-backend)
- [Configuración del entorno](#configuración-del-entorno)
- [Instalación y arranque](#instalación-y-arranque)
- [Endpoints REST y WebSocket](#endpoints-rest-y-websocket)
- [Modelos y esquemas](#modelos-y-esquemas)
- [Base de datos](#base-de-datos)
- [Estado de validación](#estado-de-validación)
- [Autor](#autor)
- [Licencia](#licencia)

## Descripción

El backend expone una API con FastAPI y persiste los datos en PostgreSQL. Sus responsabilidades principales:

1. Registrar y consultar alertas de desautenticación capturadas por los nodos ESP32.
2. Exponer los datos por endpoints REST y por un canal WebSocket en tiempo real.
3. Autenticar usuarios (JWT) y servicios (credencial máquina a máquina para la capa de procesamiento).

Para el contexto completo del sistema (arquitectura, otras capas, evidencia académica), ver el [README principal](../README.md). El [README principal también documenta el despliegue con Docker](../README.md#puesta-en-marcha), que levanta este backend junto con PostgreSQL y el frontend.

## Estructura del backend

```plaintext
backend/
├── src/
│   ├── routes/                    # Rutas HTTP y WebSocket
│   │   ├── admin_routes.py        # Vistas de administrador (/admin)
│   │   ├── alerts_summary.py      # Consultas agregadas de alertas
│   │   ├── alerts.py              # Endpoints de alertas
│   │   ├── auth.py                # Registro, login y recuperación de contraseña
│   │   ├── custom_queries.py      # Consultas predefinidas sobre alertas
│   │   ├── esp32_nodes.py         # Estado y actualización de nodos ESP32
│   │   ├── logs.py                # Lectura y descarga de logs
│   │   └── websocket.py           # Canal WebSocket en tiempo real
│   ├── services/
│   │   ├── auth_service.py        # JWT y hashing de contraseñas
│   │   └── service_auth.py        # Credencial de servicio (máquina a máquina)
│   ├── tests/                     # Pruebas
│   ├── database.py                # Configuración de la base de datos y sesiones
│   ├── main.py                    # Inicialización de la app y registro de routers
│   ├── models.py                  # Modelos ORM (SQLAlchemy)
│   ├── requirements.txt           # Dependencias, versiones fijadas
│   └── schemas.py                 # Esquemas Pydantic
├── Dockerfile
├── .dockerignore
└── README.md
```

## Configuración del entorno

### Requisitos previos

- Python 3.11, versión validada por la imagen Docker del backend.
- Git.
- PostgreSQL en ejecución (local o vía el Docker Compose del [README principal](../README.md)).

## Instalación y arranque

### 1. Clonar el repositorio y entrar al backend

```bash
git clone https://github.com/Eberth-sys/Deauth-Alert-WiFi-IoT-System.git
cd Deauth-Alert-WiFi-IoT-System/backend
```

### 2. Crear y activar un entorno virtual

```bash
python -m venv .venv
source .venv/bin/activate      # Linux/macOS
.venv\Scripts\activate         # Windows
```

### 3. Instalar dependencias

```bash
pip install --upgrade pip
pip install -r src/requirements.txt
```

### 4. Configurar las variables de entorno

```bash
cp src/.env.example src/.env
```

Completar en `src/.env`, como mínimo:

| Variable | Descripción |
| --- | --- |
| `PG_DB`, `PG_USER`, `PG_PASSWORD`, `PG_HOST`, `PG_PORT` | Conexión a PostgreSQL. El backend deriva `DATABASE_URL` de estas variables; no hace falta definirla. |
| `JWT_SECRET_KEY` | Clave para firmar los JWT. Debe tener 32 caracteres o más: el backend falla al arrancar si es más corta. |
| `SERVICE_API_KEY` | Credencial que usa la capa de procesamiento para actualizar el estado de los nodos ESP32. |
| `CORS_ORIGINS` | Orígenes permitidos, separados por coma y sin espacios (por ejemplo `http://localhost:5173,http://localhost:8080`). |
| `LOGS_DIR` | Carpeta donde se guardan los archivos de log. |
| `FRONTEND_URL` | URL del frontend, usada en enlaces generados por el backend. |

Mantener `src/.env` fuera del control de versiones (ya está en `.gitignore`).

### 5. Arrancar el servidor

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

Este es el mismo comando (sin `--reload`) que usa la imagen Docker del backend.

### 6. Ver la documentación interactiva

Con el servidor en ejecución, abrir [http://localhost:8000/docs](http://localhost:8000/docs) (Swagger UI) para explorar y probar los endpoints.

## Endpoints REST y WebSocket

`get_current_user` exige un JWT de usuario válido (encabezado `Authorization: Bearer <token>`). `get_current_admin_user` exige además rol de administrador. `verify_service_key` exige el encabezado `X-API-Key` con el valor de `SERVICE_API_KEY`.

### Autenticación (`/auth`)

| Método | Ruta | Auth | Descripción |
| --- | --- | --- | --- |
| POST | `/auth/register` | Ninguna | Registra un usuario nuevo. |
| POST | `/auth/login` | Ninguna | Inicia sesión y devuelve un JWT. |
| GET | `/auth/me` | Usuario | Devuelve los datos del usuario autenticado. |
| POST | `/auth/forgot-password` | Ninguna | Solicita la recuperación de contraseña. |
| POST | `/auth/reset-password` | Ninguna (token de reseteo en el cuerpo) | Restablece la contraseña con el token recibido. |

### Alertas y nodos

| Método | Ruta | Auth | Descripción |
| --- | --- | --- | --- |
| GET | `/alerts` | Usuario | Lista las alertas registradas. |
| GET | `/alerts-summary` | Usuario | Estadísticas agregadas de alertas. |
| GET | `/esp32-nodes` | Usuario | Lista el estado de los nodos ESP32. |
| POST | `/esp32-nodes/update` | Servicio (`X-API-Key`) | Actualiza el estado de un nodo; la capa de procesamiento la invoca y el backend emite el cambio por WebSocket. |

### Consultas personalizadas (`/custom-queries`)

| Método | Ruta | Auth | Descripción |
| --- | --- | --- | --- |
| GET | `/custom-queries/ultimas-alertas` | Usuario | Últimas alertas registradas. |
| GET | `/custom-queries/total-alertas` | Usuario | Total de alertas. |
| GET | `/custom-queries/alertas-por-nodo` | Usuario | Alertas agrupadas por nodo. |
| GET | `/custom-queries/canales-mas-afectados` | Usuario | Canales con más alertas. |
| GET | `/custom-queries/alertas-de-hoy` | Usuario | Alertas del día actual. |
| GET | `/custom-queries/alertas-por-fecha` | Usuario | Alertas filtradas por fecha. |

### Logs y administración

| Método | Ruta | Auth | Descripción |
| --- | --- | --- | --- |
| GET | `/logs` | Administrador | Lista los archivos de log. |
| GET | `/logs/{log_filename}` | Administrador | Devuelve el contenido de un log. |
| GET | `/logs/download/{log_filename}` | Administrador | Descarga el archivo de log completo. |
| GET | `/admin/logs` | Administrador | Vista de logs para administración. |
| GET | `/admin/reports` | Administrador | Vista de reportes para administración. |

### WebSocket

- **URL:** `ws://<host>:<puerto>/ws/alerts?token=<JWT>` (por ejemplo, `ws://localhost:8000/ws/alerts?token=...`).
- El token JWT viaja por parámetro de consulta, porque el WebSocket del navegador no admite encabezados personalizados en el *handshake*. Sin token válido, la conexión se rechaza con el código de cierre 1008 antes de aceptarse.
- En un despliegue expuesto a Internet, usar WSS para cifrar el token en tránsito.
- Emite en tiempo real las nuevas alertas y los cambios de estado de los nodos.

## Modelos y esquemas

| Archivo | Motor | Contenido | Descripción |
| --- | --- | --- | --- |
| `models.py` | SQLAlchemy | `Alert`, `ESP32Status` | Tablas `alerts` y `esp32_status`, con sus campos y restricciones. |
| `schemas.py` | Pydantic | `AlertCreate`, `AlertResponse`, `ESP32StatusResponse` | Validación y serialización de peticiones y respuestas. |

## Base de datos

Se usa PostgreSQL. Las tablas se crean automáticamente al iniciar la aplicación (`Base.metadata.create_all`):

| Tabla | Descripción |
| --- | --- |
| `alerts` | Eventos de desautenticación (BSSID, canal, fecha). |
| `esp32_status` | Estado (`connected`/`disconnected`) de cada nodo. |
| `users` | Cuentas de usuario del panel (creada por el propio backend). |

## Estado de validación

| Estado de validación |
| :--- |
| El backend se probó en laboratorio como parte del prototipo de tesis. Las rutas de datos y el WebSocket están protegidos con autenticación (JWT o credencial de servicio, según el endpoint); las consideraciones de seguridad y despliegue completas están en [`SECURITY.md`](../SECURITY.md). |

## Autor

**Esp. Ing. Eberth Gabriel Alarcón González.** Perfil completo, formación y evidencia académica en el [README principal](../README.md#sobre-el-autor).

## Licencia

Código y documentación propia bajo licencia Apache 2.0. Ver [LICENSE](../LICENSE) y [NOTICE](../NOTICE) en la raíz del repositorio.
