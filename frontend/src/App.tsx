//frontend\src\App.tsx

// Importamos el componente principal que muestra el resumen de alertas y estados de nodos
import DashboardPage from './pages/DashboardPage'

function App() {
  return (
    <div className="bg-gray-900 h-screen w-screen flex flex-col font-inter text-gray-100">
      {/* 🧭 Header fijo en la parte superior con sombra y desenfoque */}
      <header className="sticky top-0 z-40 bg-gray-900/80 backdrop-blur border-b border-gray-800 py-4 shadow-md">
        <h1 className="text-2xl sm:text-3xl font-extrabold text-center text-blue-400">
          🔐 Monitor de Seguridad WiFi – IoT Nodes
        </h1>
      </header>

      {/* 📦 Contenido principal */}
      <main className="flex-1 overflow-y-auto">
        <div className="max-w-screen-xl mx-auto px-4 sm:px-8 py-6">
          <DashboardPage />
        </div>
      </main>

      {/* 📜 Botón flotante para Logs */}
      <div className="fixed top-20 right-6 z-50">
        <a
          href="/logs"
          className="flex items-center gap-2 bg-white text-gray-800 px-4 py-2 rounded-full shadow-lg font-semibold hover:bg-gray-200 transition-all duration-300"
          title="Ver historial de alertas"
          aria-label="Ver Logs"
        >
          <span className="text-lg">📜</span>
          <span>Ver ble Logs</span>
        </a>
      </div>

      {/* 📅 Botón flotante para Reportes */}
      <div className="fixed top-36 right-6 z-50">
        <a
          href="/reportes"
          className="flex items-center gap-2 bg-white text-gray-800 px-4 py-2 rounded-full shadow-lg font-semibold hover:bg-gray-200 transition-all duration-300"
          title="Ver reportes personalizados"
          aria-label="Ver Reportes"
        >
          <span className="text-lg">📅</span>
          <span>Ver Reportes</span>
        </a>
      </div>

      {/* Botón flotante para acceder a las estadísticas */}
      <div className="fixed top-52 right-6 z-50">
        <a
          href="/estadisticas"
          className="flex items-center gap-2 bg-white text-gray-800 px-4 py-2 rounded-full shadow-lg font-semibold hover:bg-gray-200 transition-all duration-300"
          title="Ver estadísticas generales"
          aria-label="Ver Estadísticas"
        >
          <span className="text-lg">📈</span>
          <span>Estadísticas</span>
        </a>
      </div>

      {/* 📄 Footer */}
      <footer className="text-center text-xs text-gray-500 py-4 border-t border-gray-800">
        © {new Date().getFullYear()} Sistema IoT para el monitoreo y detección de ataques de desautenticación en redes Wi-Fi – Eberth Alarcón
      </footer>
    </div>
  )
}

export default App
