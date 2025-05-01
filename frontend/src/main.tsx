//frontend\src\main.tsx

// -------------------- Importaciones principales --------------------
import { StrictMode } from "react";                        // Modo estricto de React para detectar problemas
import { createRoot } from "react-dom/client";             // Punto de entrada para React 18+
import "./index.css";                                      // Estilos globales

// -------------------- Enrutamiento --------------------
import { BrowserRouter, Routes, Route } from "react-router-dom";

// -------------------- Páginas --------------------
import App from "./App.tsx";                               // Dashboard principal
import LogsPage from "./pages/LogsPage.tsx";
import ReportsPage from "./pages/ReportsPage.tsx";
import StatisticsPage from "./pages/StatisticsPage";
import LoginPage from "./pages/LoginPage.tsx";
import RegisterPage from "./pages/RegisterPage.tsx";
import ForgotPasswordPage from "./pages/ForgotPasswordPage.tsx";
import ResetPasswordPage from "./pages/ResetPasswordPage.tsx";

// -------------------- Contexto y rutas protegidas --------------------
import { AuthProvider } from "./context/AuthContext";       // Proveedor global de autenticación
import PrivateRoute from "./routes/PrivateRoute";           // Envoltura para proteger rutas privadas

// -------------------- Renderizado de la aplicación --------------------
createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <AuthProvider>              {/* 🔐 Provee el contexto de sesión a toda la app */}
      <BrowserRouter>
        <Routes>
          {/* 🔓 Rutas públicas */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/forgot-password" element={<ForgotPasswordPage />} />
          <Route path="/reset-password" element={<ResetPasswordPage />} />

          {/* 🔐 Rutas protegidas: requieren sesión activa */}
          <Route path="/" element={<PrivateRoute><App /></PrivateRoute>} />
          <Route path="/logs" element={<PrivateRoute><LogsPage /></PrivateRoute>} />
          <Route path="/reportes" element={<PrivateRoute><ReportsPage /></PrivateRoute>} />
          <Route path="/estadisticas" element={<PrivateRoute><StatisticsPage /></PrivateRoute>} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  </StrictMode>
);
