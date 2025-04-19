//frontend\src\main.tsx

// Importa modo estricto de React para detectar posibles errores en desarrollo
import { StrictMode } from 'react'

// Crea el punto de montaje raíz con React 18+
import { createRoot } from 'react-dom/client'

// Estilos globales
import './index.css'

// Importa enrutador y componentes de ruta
import { BrowserRouter, Routes, Route } from 'react-router-dom'

// Importación de las páginas principales del sistema
import App from './App.tsx'
import LogsPage from './pages/LogsPage.tsx'
import ReportsPage from './pages/ReportsPage.tsx'
import StatisticsPage from './pages/StatisticsPage'

// Monta el componente principal en el div con id="root"
createRoot(document.getElementById('root')!).render(
  <StrictMode>
    {/* Envolvemos la aplicación con el manejador de rutas */}
    <BrowserRouter>
      <Routes>
        {/* Página principal: Dashboard */}
        <Route path="/" element={<App />} />

        {/* Página de visualización de logs */}
        <Route path="/logs" element={<LogsPage />} />

        {/* Página de reportes personalizados */}
        <Route path="/reportes" element={<ReportsPage />} />

        {/* Página de estadísticas generales */}
        <Route path="/estadisticas" element={<StatisticsPage />} />
      </Routes>
    </BrowserRouter>
  </StrictMode>
)
