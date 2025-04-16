// frontend/src/App.tsx
import AlertHeatmapTable from './components/AlertHeatmapTable'

function App() {
  return (
    <div className="bg-gray-900 h-screen w-screen flex flex-col">
      {/* Cabecera */}
      <header className="py-6">
        <h1 className="text-4xl font-extrabold text-center text-blue-400">
          Dashboard IoT – Alertas
        </h1>
      </header>

      {/* Contenido principal */}
      <main className="flex-1 overflow-y-auto">
        <AlertHeatmapTable />
      </main>

      {/* 🔘 Botón flotante con icono y texto */}
      <div className="fixed top-20 right-6 z-50">
        <a
          href="/logs"
          className="flex items-center gap-2 bg-white text-gray-800 px-4 py-2 rounded-full shadow-lg font-semibold hover:bg-gray-200 transition-all duration-300"
        >
          <span className="text-lg">📜</span>
          <span>Ver Logs</span>
        </a>
      </div>
    </div>
  )
}

export default App

