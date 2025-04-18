//frontend\src\App.tsx

// Importamos el componente principal que muestra el resumen de alertas y estados de nodos
import AlertHeatmapTable from './components/AlertHeatmapTable'

function App() {
  return (
    // Contenedor general con fondo oscuro, fuente personalizada y texto claro
    <div className="bg-gray-900 h-screen w-screen flex flex-col font-inter text-gray-100">
      
      {/* 🧭 Header fijo en la parte superior con sombra y desenfoque */}
      <header className="sticky top-0 z-40 bg-gray-900/80 backdrop-blur border-b border-gray-800 py-4 shadow-md">
        <h1 className="text-2xl sm:text-3xl font-extrabold text-center text-blue-400">
          🔐 Monitor de Seguridad WiFi – IoT Nodes
        </h1>
      </header>

      {/* 📦 Contenido principal centrado, con padding adaptable */}
      <main className="flex-1 overflow-y-auto">
        <div className="max-w-screen-xl mx-auto px-4 sm:px-8 py-6">
          <AlertHeatmapTable />
        </div>
      </main>

      {/* 📜 Botón flotante fijo para acceder al visor de logs */}
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

      {/* 📄 Footer descriptivo al final de la página */}
      <footer className="text-center text-xs text-gray-500 py-4 border-t border-gray-800">
        © {new Date().getFullYear()} Sistema IoT para el monitoreo y detección de ataques de desautenticación en redes Wi-Fi – Eberth Alarcón
      </footer>
    </div>
  )
}

export default App
