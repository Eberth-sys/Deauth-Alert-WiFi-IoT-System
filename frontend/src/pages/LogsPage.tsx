// frontend/src/pages/LogsPage.tsx

// Importamos hooks de React
import { useEffect, useState } from 'react'

// Importamos funciones utilitarias y componentes personalizados
import { fetchLogFile, downloadLogFile, getLineColor } from '../components/utils/logs'
import LogViewer from '../components/LogViewer'
import DownloadButton from '../components/DownloadButton'

// Definimos el nombre del archivo de logs a visualizar
const LOG_FILE = 'ble_events.log'

// Componente principal de la página de logs
const LogsPage = () => {
  // Estado para guardar las líneas del archivo de log
  const [logLines, setLogLines] = useState<string[]>([])

  // Estado para capturar posibles errores
  const [error, setError] = useState<string | null>(null)

  // Efecto que se ejecuta al montar el componente (una sola vez)
  useEffect(() => {
    // Cargamos el archivo usando la función utilitaria
    fetchLogFile(LOG_FILE)
      .then(setLogLines)                      // Guardamos las líneas si todo va bien
      .catch(() => setError('❌ Error al cargar el archivo de logs')) // En caso de error, lo registramos
  }, [])

  // Render del componente
  return (
    <div className="bg-gray-900 h-screen w-screen flex flex-col">
      
      {/* Cabecera con botón de regreso a la página principal */}
      <header className="bg-gray-800 shadow-md py-4 px-6 flex items-center justify-start">
        <a href="/" className="text-white font-bold text-lg flex items-center gap-2 hover:text-blue-400 transition">
          <span>🏠</span> Inicio
        </a>
      </header>

      {/* Contenido principal */}
      <main className="flex-1 overflow-y-auto px-4 py-8 flex flex-col items-center">

        {/* Título con línea inferior decorativa */}
        <div className="border-b border-blue-500 mb-6 pb-2 w-full max-w-4xl text-center">
          <h2 className="text-3xl font-extrabold text-blue-400">
            Visualizador de Logs BLE
          </h2>
        </div>

        {/* Botón para descargar los logs, usando componente externo */}
        <DownloadButton onClick={() => downloadLogFile(LOG_FILE, logLines)} />

        {/* Componente que muestra las líneas del log o el error */}
        <LogViewer lines={logLines} error={error} />
      </main>
    </div>
  )
}

// Exportamos el componente para poder usarlo en la app
export default LogsPage
