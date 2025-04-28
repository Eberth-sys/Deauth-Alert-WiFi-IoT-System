// Importamos el componente principal que muestra el resumen de alertas y estados de nodos
import DashboardPage from './pages/DashboardPage'
import Footer from './components/Footer'

function App() {
  return (
    <div className="bg-gray-900 h-screen w-screen flex flex-col font-inter text-gray-100">
      {/* 🧭 Header fijo en la parte superior con sombra y desenfoque */}
      <header className="sticky top-0 z-40 bg-gray-900/80 backdrop-blur border-b border-gray-800 py-4 shadow-md">
        <h1 className="text-2xl sm:text-3xl font-extrabold text-center text-blue-400">
           🛜 Monitor de seguridad Wi-Fi 2,4 Ghz 🔐
        </h1>
      </header>

      {/* 📦 Contenido principal */}
      <main className="flex-1 overflow-y-auto">
        <div className="max-w-screen-xl mx-auto px-4 sm:px-8 py-6">
          <DashboardPage />
        </div>
      </main>

      {/* 🧭 Botones flotantes - Escritorio */}
      <div className="fixed z-50 right-6 top-24 flex flex-col gap-3 sm:flex hidden">
        <a
          href="/logs"
          className="flex items-center gap-2 bg-white text-gray-800 px-4 py-2 rounded-full shadow-lg font-semibold hover:bg-gray-200 transition-all duration-300"
          title="Ver historial de alertas"
          aria-label="Ver Logs"
        >
          <span className="text-lg">📜</span>
          <span>Ver BLE logs</span>
        </a>
        <a
          href="/reportes"
          className="flex items-center gap-2 bg-white text-gray-800 px-4 py-2 rounded-full shadow-lg font-semibold hover:bg-gray-200 transition-all duration-300"
          title="Ver reportes personalizados"
          aria-label="Ver Reportes"
        >
          <span className="text-lg">📅</span>
          <span>Ver reportes</span>
        </a>
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

      {/* 📱 Botones móviles - Barra inferior */}
      <div className="fixed z-50 bottom-4 left-1/2 -translate-x-1/2 w-[95%] flex justify-around sm:hidden">
        <a
          href="/logs"
          title="Logs"
          className="bg-white text-gray-800 px-3 py-2 rounded-full shadow-md text-sm font-semibold flex items-center gap-1"
        >
          📜
        </a>
        <a
          href="/reportes"
          title="Reportes"
          className="bg-white text-gray-800 px-3 py-2 rounded-full shadow-md text-sm font-semibold flex items-center gap-1"
        >
          📅
        </a>
        <a
          href="/estadisticas"
          title="Estadísticas"
          className="bg-white text-gray-800 px-3 py-2 rounded-full shadow-md text-sm font-semibold flex items-center gap-1"
        >
          📈
        </a>
      </div>

      {/* 📄 Footer - Pie de página*/}
      <Footer />
    </div>
  )
}

export default App
