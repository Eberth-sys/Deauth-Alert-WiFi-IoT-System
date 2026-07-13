> 🌐 **[English](README.en.md)** · **Español**

# Frontend

⬅ Parte de [Deauth-Alert](../README.md)

<p align="left">
  <img alt="React" src="https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black">
  <img alt="TypeScript" src="https://img.shields.io/badge/TypeScript-5.7-3178C6?logo=typescript&logoColor=white">
  <img alt="Vite" src="https://img.shields.io/badge/Vite-6-646CFF?logo=vite&logoColor=white">
  <img alt="Tailwind" src="https://img.shields.io/badge/Tailwind-4-06B6D4?logo=tailwindcss&logoColor=white">
  <img alt="Licencia" src="https://img.shields.io/badge/licencia-Apache%202.0-blue">
</p>

Manual técnico del frontend: panel en React que muestra en tiempo real las alertas de desautenticación capturadas por los nodos ESP32.

## Índice

- [Descripción](#descripción)
- [Estructura del frontend](#estructura-del-frontend)
- [Configuración del entorno](#configuración-del-entorno)
- [Instalación y arranque](#instalación-y-arranque)
- [Uso y navegación](#uso-y-navegación)
- [Estado de validación](#estado-de-validación)
- [Autor](#autor)
- [Licencia](#licencia)

## Descripción

El frontend de Deauth-Alert ofrece una interfaz para visualizar y gestionar en tiempo real las alertas de desautenticación. Desarrollado con React, TypeScript, TailwindCSS y Vite, incluye:

1. Panel con indicadores de estado y métricas.
2. Gestión de registros: filtrado, búsqueda y descarga de logs.
3. Reportes y gráficas históricas exportables en CSV.
4. Autenticación y manejo de sesiones.
5. Notificaciones en tiempo real por WebSocket.

Para el contexto completo del sistema (arquitectura, otras capas, evidencia académica), ver el [README principal](../README.md). El [README principal también documenta el despliegue con Docker](../README.md#puesta-en-marcha), que levanta este frontend junto con el backend y PostgreSQL.

## Estructura del frontend

<details>
<summary>Ver árbol completo</summary>

```plaintext
frontend/
├── public/
│   └── sounds/                          # Sonidos de notificación y advertencia
├── src/
│   ├── assets/                          # Imágenes y SVG
│   ├── auth/                            # Lógica y componentes de autenticación
│   ├── components/                      # Componentes reutilizables de la interfaz
│   ├── context/                         # Contexto de la aplicación (p. ej. AuthContext)
│   ├── hooks/                           # Hooks personalizados (alertas, autenticación, conexión de nodos)
│   ├── pages/                           # Páginas: Dashboard, Login, Register, Logs, Reports, Statistics
│   ├── routes/                          # PrivateRoute (rutas que requieren autenticación)
│   ├── services/                        # Conexión al backend (auth, reportes, WebSocket, estadísticas)
│   ├── types/                           # Tipos TypeScript
│   ├── utils/                           # Utilidades (descargas, formateo, logs, validación)
│   ├── App.tsx
│   ├── index.css
│   └── main.tsx
├── .env.example
├── Dockerfile
├── nginx.conf
├── package.json
└── vite.config.ts
```

</details>

## Configuración del entorno

### Requisitos previos

- Node.js 18 o superior (recomendado 20 LTS). Vite 6 requiere Node 18+.
- npm o yarn.
- Git.

## Instalación y arranque

### 1. Clonar el repositorio

```bash
git clone https://github.com/Eberth-sys/Deauth-Alert-WiFi-IoT-System.git
cd Deauth-Alert-WiFi-IoT-System/frontend
```

### 2. Instalar dependencias

```bash
npm install
```

Todas las dependencias del proyecto (incluidas `react-router-dom`, `@melloware/react-logviewer` y `@heroicons/react`) están declaradas en `package.json`; no hace falta instalarlas por separado.

### 3. Configurar las variables de entorno

```bash
cp .env.example .env
```

Ajustar `VITE_BACKEND_URL` y `VITE_WS_URL` según la URL del backend.

### 4. Ejecutar en modo desarrollo

```bash
npm run dev
```

Abrir [http://localhost:5173](http://localhost:5173).

### 5. Compilar para producción

```bash
npm run build
```

## Uso y navegación

| Ruta | Página |
| --- | --- |
| `/login`, `/register` | Inicio de sesión y registro. |
| `/forgot-password` | Solicitud de recuperación de contraseña. |
| `/reset-password` | Restablecimiento de contraseña con token. |
| `/` | Panel principal, con estadísticas y estado de los nodos (requiere sesión). |
| `/logs` | Filtrado, visualización y descarga de logs (requiere sesión). |
| `/reportes` | Reportes descargables en CSV (requiere sesión). |
| `/estadisticas` | Gráficas interactivas (requiere sesión). |

## Estado de validación

| Estado de validación |
| :--- |
| El frontend se probó en laboratorio como parte del prototipo de tesis, junto con el backend y los nodos ESP32. |

## Autor

**Esp. Ing. Eberth Gabriel Alarcón González.** Perfil completo, formación y evidencia académica en el [README principal](../README.md#sobre-el-autor).

## Licencia

Código y documentación propia bajo licencia Apache 2.0. Ver [LICENSE](../LICENSE) y [NOTICE](../NOTICE) en la raíz del repositorio.
