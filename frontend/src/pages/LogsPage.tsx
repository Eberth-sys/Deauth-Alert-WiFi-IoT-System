// frontend\src\pages\LogsPage.tsx

// Importa hooks de React para gestionar estado y efectos
import { useEffect, useState } from 'react'

// Importa funciones utilitarias para manejar archivos de log
import { fetchLogFile, downloadLogFile } from '../components/utils/logs'

// Importa componentes personalizados
import LogViewer from '../components/LogViewer'
import DownloadButton from '../components/DownloadButton'
import LogFilters from '../components/LogFilters'
import ReloadButton from '../components/ReloadButton'

// Nombre del archivo de log a mostrar
const LOG_FILE = 'ble_events.log'

// Componente principal de la página de visualización de logs
const LogsPage = () => {
  // Estado para guardar las líneas del archivo log
  const [logLines, setLogLines] = useState<string[]>([])

  // Estado para mostrar errores si ocurre alguno al cargar logs
  const [error, setError] = useState<string | null>(null)

  // Estado para filtrar logs por nivel (INFO, WARNING, ERROR, etc.)
  const [selectedLevel, setSelectedLevel] = useState<'ALL' | 'INFO' | 'WARNING' | 'ERROR' | 'CRITICAL'>('ALL')

  // Función para cargar (o recargar) el archivo de logs desde el backend
  const handleReload = () => {
    fetchLogFile(LOG_FILE)
      .then(setLogLines) // Almacena las líneas en el estado
      .catch(() => setError('❌ Error al cargar el archivo de logs')) // Manejo de error
  }

  // Se ejecuta una sola vez al montar el componente para cargar los logs
  useEffect(() => {
    handleReload()
  }, [])

  return (
    <div className="bg-gray-900 h-screen w-screen flex flex-col">
      {/* Header completamente expandido con botón alineado a la derecha */}
      <header className="bg-gray-800 shadow-md py-4 px-6 w-full flex justify-end">
        <a
          href="/"
          className="text-white font-bold text-lg flex items-center gap-2 hover:text-blue-400 transition"
        >
          <span className="text-xl">🏠</span>
          <span className="text-sm sm:text-base">Volver al Inicio</span>
        </a>
      </header>

      {/* Área principal de la página */}
      <main className="flex-1 overflow-y-auto px-4 py-8 flex flex-col items-center">

        {/* Título de la sección */}
        <div className="border-b border-blue-500 mb-6 pb-2 w-full max-w-4xl text-center">
          <h2 className="text-3xl font-extrabold text-blue-400">Visualizador de Logs BLE</h2>
        </div>

        {/* Filtros para mostrar logs por nivel de severidad */}
        <LogFilters
          selectedLevel={selectedLevel}
          onSelectLevel={setSelectedLevel}
        />

        {/* Botones para descargar o recargar los logs */}
        <div className="flex gap-4 mb-6">
          <DownloadButton onClick={() => downloadLogFile(LOG_FILE, logLines)} />
          <ReloadButton onClick={handleReload} />
        </div>

        {/* Componente que muestra las líneas del archivo */}
        <LogViewer
          lines={logLines}
          error={error}
          selectedLevel={selectedLevel}
        />
      </main>
    </div>
  )
}

export default LogsPage
