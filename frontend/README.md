# 🚀 Frontend | Deauth‑Alert Wi‑Fi IoT System <!-- omit in toc -->

## 🗂️ Índice <!-- omit in toc -->

<!-- TOC levels="2..4" -->

- [🖥️ Descripción](#️-descripción)
- [📂 Estructura del frontend](#-estructura-del-frontend)
- [⚙️ Configuración del entorno](#️-configuración-del-entorno)
  - [📋 Requisitos previos](#-requisitos-previos)
- [🔧 Instalación y arranque](#-instalación-y-arranque)
- [📐 Uso y navegación](#-uso-y-navegación)
- [👨‍💻 **Autor**](#-autor)
- [📄 Licencia](#-licencia)

## 🖥️ Descripción

El **frontend** de Deauth‑Alert Wi‑Fi IoT System ofrece una interfaz interactiva y responsiva para visualizar y gestionar en tiempo real las alertas de desautenticación capturadas por los nodos ESP32. Desarrollado con **React**, **TypeScript**, **Tailwind CSS** y **Vite**, incorpora:

1. Dashboard dinámico con indicadores de estado y métricas.
2. Gestión de registros (filtrado, búsqueda y descarga de logs).
3. Reportes y gráficas históricas exportables en CSV.
4. Autenticación segura y manejo de sesiones.
5. Notificaciones en tiempo real via WebSocket.

## 📂 Estructura del frontend

```plaintext
frontend/                                # Directorio principal del frontend del proyecto.
├── node_modules/                        # Carpeta donde se almacenan todas las dependencias de Node.js.
├── public/                              # Carpeta pública que contiene archivos accesibles directamente desde el navegador.
│   └── sounds/                          # Subcarpeta para archivos de sonido utilizados en el frontend.
│       ├── notification.mp3             # Archivo de sonido para notificaciones.
│       ├── warning.mp3                  # Archivo de sonido para advertencias.
│       └── vite.svg                     # Ícono SVG de Vite (probablemente utilizado en la interfaz).
├── src/                                 # Carpeta fuente que contiene el código fuente de la aplicación.
│   ├── assets/                          # Carpeta de recursos como imágenes y SVGs.
│   │   └── react.svg                    # Ícono de React utilizado en la interfaz.
│   ├── auth/                            # Carpeta de autenticación para lógica y componentes relacionados.
│   ├── components/                      # Carpeta que contiene los componentes reutilizables de la interfaz.
│   │   ├── AlertNotification.tsx        # Componente que maneja la notificación de alerta.
│   │   ├── AlertRow.tsx                 # Componente que muestra una fila de alerta en una tabla.
│   │   ├── AlertSummaryTable.tsx        # Componente que muestra un resumen de alertas en una tabla.
│   │   ├── BackToHomeButton.tsx         # Componente de botón para volver a la página de inicio.
│   │   ├── ConnectionNotification.tsx   # Componente para mostrar la notificación de estado de conexión.
│   │   ├── DownloadButton.tsx           # Componente para descargar archivos desde el frontend.
│   │   ├── Footer.tsx                   # Componente para el pie de página.
│   │   ├── LatestAlertsTable.tsx        # Componente para mostrar una tabla con las últimas alertas.
│   │   ├── LogFilters.tsx               # Componente para los filtros de los logs.
│   │   ├── LogoutButton.tsx             # Componente de botón para cerrar sesión.
│   │   ├── LogViewer.tsx                # Componente para ver los logs.
│   │   ├── NodeStatusTable.tsx          # Componente para mostrar el estado de los nodos.
│   │   ├── PasswordInput.tsx            # Componente de entrada para la contraseña.
│   │   ├── PasswordRequirements.tsx     # Componente que muestra los requisitos de la contraseña.
│   │   ├── ReloadButton.tsx             # Componente para recargar la página o datos.
│   │   ├── ReportsTable.tsx             # Componente para mostrar los reportes en una tabla.
│   │   └── StatsCard.tsx                # Componente para mostrar las estadísticas en formato de tarjeta.
│   │   ├── StatsTable.tsx               # Componente para mostrar las estadísticas en formato de tabla.
│   │   └── TableHeader.tsx              # Componente para el encabezado de la tabla.
│   ├── context/                          # Carpeta para el manejo del contexto de la aplicación (como el contexto de autenticación).
│   │   └── AuthContext.tsx              # Componente que maneja el contexto de autenticación (usuario logueado).
│   ├── hooks/                            # Carpeta para almacenar hooks personalizados.
│   │   ├── useAlertWatcher.ts           # Hook que observa las alertas activas.
│   │   ├── useAuth.ts                   # Hook para gestionar el estado de autenticación.
│   │   └── useNodeConnectionWatcher.ts  # Hook para gestionar la conexión a los nodos IoT.
│   ├── pages/                            # Carpeta para las páginas principales de la aplicación.
│   │   ├── DashboardPage.tsx            # Página principal del panel de control (Dashboard).
│   │   ├── ForgotPasswordPage.tsx       # Página para recuperar la contraseña.
│   │   ├── LoginPage.tsx                # Página de inicio de sesión.
│   │   ├── LogsPage.tsx                 # Página para visualizar los logs.
│   │   ├── PublicLayout.tsx             # Componente de disposición pública (estructura general de las páginas).
│   │   ├── RegisterPage.tsx             # Página de registro de nuevos usuarios.
│   │   ├── ReportsPage.tsx              # Página que muestra los reportes.
│   │   ├── ResetPasswordPage.tsx        # Página para restablecer la contraseña.
│   │   └── StatisticsPage.tsx           # Página para mostrar estadísticas.
│   ├── routes/                           # Carpeta para las rutas de la aplicación.
│   │   └── PrivateRoute.tsx             # Componente para gestionar rutas privadas (requiere autenticación).
│   ├── services/                         # Carpeta para la lógica de servicios (conexión a backend y lógica de negocio).
│   │   ├── auth.ts                      # Servicio para gestionar la autenticación del usuario.
│   │   ├── reports.ts                   # Servicio para gestionar los reportes.
│   │   ├── socket.ts                    # Servicio para gestionar las conexiones WebSocket.
│   │   └── stats.ts                     # Servicio para obtener las estadísticas.
│   ├── types/                            # Carpeta para los tipos de datos y definiciones TypeScript.
│   │   └── index.ts                     # Archivo principal de tipos.
│   ├── utils/                            # Carpeta para utilidades generales.
│   │   ├── download.ts                  # Funciones para gestionar descargas.
│   │   ├── formatters.ts                # Funciones para formatear datos (como fechas y números).
│   │   ├── logs.ts                      # Funciones para manejar logs.
│   │   └── validators.ts                # Funciones para validar formularios y datos de entrada.
│   ├── App.tsx                          # Componente raíz de la aplicación que estructura y organiza otros componentes.
│   ├── index.css                        # Estilos CSS globales para la aplicación.
│   ├── main.tsx                         # Archivo principal de la aplicación que monta el componente `App`.
│   └── vite-env.d.ts                    # Definición de tipos para Vite.
├── .env                                 # Archivo de configuración de variables de entorno (como las URLs del backend).
├── .env.example                         # Ejemplo del archivo `.env` con variables de entorno.
├── .gitignore                           # Archivo que indica qué archivos o carpetas no deben ser seguidos por Git.
├── eslint.config.js                     # Configuración de ESLint para la aplicación.
├── index.html                           # Archivo HTML principal.
├── package-lock.json                    # Archivo generado automáticamente que asegura la integridad de las dependencias.
├── package.json                         # Archivo de configuración de dependencias y scripts del proyecto.
├── postcss.config.cjs                   # Configuración de PostCSS para el manejo de CSS.
├── README.md                            # Documento que describe el proyecto.
├── tailwind.config.ts                   # Configuración de TailwindCSS para el estilo de la aplicación.
├── tsconfig.app.json                    # Configuración de TypeScript para la aplicación.
├── tsconfig.json                        # Configuración principal de TypeScript para todo el proyecto.
├── tsconfig.node.json                   # Configuración de TypeScript específica para nodos.
└── vite.config.ts                       # Configuración de Vite (el empaquetador de módulos).

```

## ⚙️ Configuración del entorno

### 📋 Requisitos previos

* **Node.js** v14 o superior
* **npm** o **yarn**
* **Git** para control de versiones

## 🔧 Instalación y arranque

1. **Clonar el repositorio**:

   ```bash
   git clone https://github.com/Eberth-sys/Deauth-Alert-WiFi-IoT-System.git
   cd Deauth-Alert-WiFi-IoT-System/frontend
   ```
2. **Instalar dependencias**:

   ```bash
   npm install
   # o
   yarn install
   ```

   Además, instalar librerías adicionales:

   ```bash
   npm install react-router-dom
   npm install @melloware/react-logviewer
   npm install @heroicons/react
   # Tipos para react-router-dom
   npm install --save-dev @types/react-router-dom
   ```

    ```bash
      npm install
      # o
      yarn install
    ```

3. **Configurar variables de entorno**:

   ```bash
   cp .env.example .env
   ```

   * Ajustar `VITE_BACKEND_URL` y `VITE_WS_URL` según la URL del servicio backend.
4. **Ejecutar en modo desarrollo**:

   ```bash
   npm run dev
   # o
   yarn dev
   ```

   * Visitar [http://localhost:5173](http://localhost:5173)
5. **Construcción para producción**:

   ```bash
   npm run build
   ```

## 📐 Uso y navegación

* **Inicio de sesión / Registro**: `/login` y `/register`.
* **Dashboard**: `/dashboard` muestra estadísticas y estado de nodos.
* **Registros**: `/logs` permite filtrar, visualizar y descargar logs.
* **Reportes**: `/reports` descarga datos en CSV.
* **Estadísticas**: `/statistics` muestra gráficas interactivas.

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