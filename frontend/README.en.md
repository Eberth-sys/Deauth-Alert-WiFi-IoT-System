> 🌐 **English** · **[Español](README.md)**

# Frontend

⬅ Part of [Deauth-Alert](../README.en.md)

<p align="left">
  <img alt="React" src="https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black">
  <img alt="TypeScript" src="https://img.shields.io/badge/TypeScript-5.7-3178C6?logo=typescript&logoColor=white">
  <img alt="Vite" src="https://img.shields.io/badge/Vite-6-646CFF?logo=vite&logoColor=white">
  <img alt="Tailwind" src="https://img.shields.io/badge/Tailwind-4-06B6D4?logo=tailwindcss&logoColor=white">
  <img alt="License" src="https://img.shields.io/badge/license-Apache%202.0-blue">
</p>

Frontend technical manual: a React dashboard that displays, in real time, the deauthentication alerts captured by the ESP32 nodes.

## Table of Contents

- [Overview](#overview)
- [Frontend Structure](#frontend-structure)
- [Environment Configuration](#environment-configuration)
- [Installation and Startup](#installation-and-startup)
- [Usage and Navigation](#usage-and-navigation)
- [Validation Status](#validation-status)
- [Author](#author)
- [License](#license)

## Overview

The Deauth-Alert frontend provides an interface for visualizing and managing deauthentication alerts in real time. Built with React, TypeScript, TailwindCSS, and Vite, it includes:

1. A dashboard with status indicators and metrics.
2. Log management: filtering, search, and log downloads.
3. Reports and historical charts that can be exported to CSV.
4. Authentication and session handling.
5. Real-time notifications over WebSocket.

For the full system context (architecture, other layers, academic evidence), see the [main README](../README.en.md). The [main README also documents the Docker deployment](../README.en.md#getting-started), which brings up this frontend together with the backend and PostgreSQL.

## Frontend Structure

<details>
<summary>View full tree</summary>

```plaintext
frontend/
├── public/
│   └── sounds/                          # Notification and warning sounds
├── src/
│   ├── assets/                          # Images and SVGs
│   ├── auth/                            # Authentication logic and components
│   ├── components/                      # Reusable UI components
│   ├── context/                         # Application context (e.g. AuthContext)
│   ├── hooks/                           # Custom hooks (alerts, authentication, node connection)
│   ├── pages/                           # Pages: Dashboard, Login, Register, Logs, Reports, Statistics
│   ├── routes/                          # PrivateRoute (routes that require authentication)
│   ├── services/                        # Backend connection (auth, reports, WebSocket, statistics)
│   ├── types/                           # TypeScript types
│   ├── utils/                           # Utilities (downloads, formatting, logs, validation)
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

## Environment Configuration

### Prerequisites

- Node.js 18 or later (20 LTS recommended). Vite 6 requires Node 18+.
- npm or yarn.
- Git.

## Installation and Startup

### 1. Clone the repository

```bash
git clone https://github.com/Eberth-sys/Deauth-Alert-WiFi-IoT-System.git
cd Deauth-Alert-WiFi-IoT-System/frontend
```

### 2. Install dependencies

```bash
npm install
```

All project dependencies (including `react-router-dom`, `@melloware/react-logviewer`, and `@heroicons/react`) are declared in `package.json`; there is no need to install them separately.

### 3. Configure the environment variables

```bash
cp .env.example .env
```

Set `VITE_BACKEND_URL` and `VITE_WS_URL` to match the backend URL.

### 4. Run in development mode

```bash
npm run dev
```

Open [http://localhost:5173](http://localhost:5173).

### 5. Build for production

```bash
npm run build
```

## Usage and Navigation

| Route | Page |
| --- | --- |
| `/login`, `/register` | Sign-in and registration. |
| `/forgot-password` | Password recovery request. |
| `/reset-password` | Password reset with a token. |
| `/` | Main dashboard, with statistics and node status (requires a session). |
| `/logs` | Log filtering, viewing, and downloading (requires a session). |
| `/reportes` | Reports downloadable as CSV (requires a session). |
| `/estadisticas` | Interactive charts (requires a session). |

## Validation Status

| Validation Status |
| :--- |
| The frontend was tested in the lab as part of the thesis prototype, together with the backend and the ESP32 nodes. |

## Author

**Esp. Ing. Eberth Gabriel Alarcón González.** Full profile, education, and academic evidence in the [main README](../README.en.md#about-the-author).

## License

Original code and documentation under the Apache 2.0 license. See [LICENSE](../LICENSE) and [NOTICE](../NOTICE) at the root of the repository.
