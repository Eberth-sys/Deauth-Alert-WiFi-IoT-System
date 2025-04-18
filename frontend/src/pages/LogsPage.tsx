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
import BackToHomeButton from '../components/BackToHomeButton'

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
      <main className="flex-1 overflow-y-auto px-4 py-8 flex flex-col items-center">

      <div className="relative w-full mb-6">
        {/* Título centrado */}
        <h2 className="text-5xl font-extrabold text-blue-400 text-center animate-pulse drop-shadow-[0_0_10px_rgba(59,130,246,0.7)]">
          Visualizador de Logs BLE
        </h2>

        {/* Botón completamente a la derecha */}
          <div className="absolute top-0 right-0">
            <BackToHomeButton />
          </div>
        </div>

        {/* Filtro por nivel */}
        <LogFilters selectedLevel={selectedLevel} onSelectLevel={setSelectedLevel} />

        {/* Botones de acción */}
        <div className="flex gap-4 mb-6">
          <DownloadButton onClick={() => downloadLogFile(LOG_FILE, logLines)} />
          <ReloadButton onClick={handleReload} />
        </div>

        {/* Visor de logs */}
        <LogViewer lines={logLines} error={error} selectedLevel={selectedLevel} />
      </main>
    </div>
  )
}

export default LogsPage
