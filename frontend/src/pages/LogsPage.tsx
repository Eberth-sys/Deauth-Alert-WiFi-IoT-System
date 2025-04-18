// frontend/src/pages/LogsPage.tsx

// Importamos hooks de React
import { useEffect, useState } from 'react'

// Importamos funciones utilitarias y componentes personalizados
import { fetchLogFile, downloadLogFile } from '../components/utils/logs'
import LogViewer from '../components/LogViewer'


// Definimos el nombre del archivo de logs a visualizar
const LOG_FILE = 'ble_events.log'

// Componente principal de la página de logs
const LogsPage = () => {
  // Estado para guardar las líneas del archivo de log
  const [logLines, setLogLines] = useState<string[]>([])

  // Estado para capturar posibles errores
  const [error, setError] = useState<string | null>(null)

  // Carga inicial de logs al montar
  useEffect(() => {
    handleReload()
  }, [])

  // Función para recargar logs manualmente
  const handleReload = () => {
    fetchLogFile(LOG_FILE)
      .then(setLogLines)
      .catch(() => setError('❌ Error al cargar el archivo de logs'))
  }

  return (
    <div className="bg-gray-900 h-screen w-screen flex flex-col">
      
     {/* Header superior con botón alineado a la derecha */}
      <header className="bg-gray-800 shadow-md py-4 px-6 w-full">
        <div className="flex justify-end items-center w-full max-w-screen-xl mx-auto">
          <a
            href="/"
            className="text-white font-bold text-lg flex items-center gap-2 hover:text-blue-400 transition"
          >
            <span className="text-xl">🏠</span>
            <span className="text-sm sm:text-base">Volver al Inicio</span>
          </a>
        </div>
      </header>

      {/* Main content */}
      <main className="flex-1 overflow-y-auto px-4 py-8 flex flex-col items-center">
        
        {/* Título */}
        <div className="border-b border-blue-500 mb-6 pb-2 w-full max-w-4xl text-center">
          <h2 className="text-3xl font-extrabold text-blue-400">
            Visualizador de Logs BLE
          </h2>
        </div>

        {/* Botones de acción */}
        <div className="flex flex-wrap justify-center gap-4 mb-6">
          <button
            onClick={() => downloadLogFile(LOG_FILE, logLines)}
            className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-6 rounded-lg shadow-md transition-all duration-200"
          >
            📥 Descargar archivo Logs
          </button>

          <button
            onClick={handleReload}
            className="bg-yellow-500 hover:bg-yellow-600 text-white font-semibold py-2 px-6 rounded-lg shadow-md transition-all duration-200"
          >
            🔄 Recargar logs
          </button>
        </div>

        {/* Log Viewer */}
        <LogViewer lines={logLines} error={error} />
      </main>
    </div>
  )
}
export default LogsPage
