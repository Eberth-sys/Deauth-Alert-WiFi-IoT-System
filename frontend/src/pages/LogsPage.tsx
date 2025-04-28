import { useEffect, useState } from 'react'
import { fetchLogFile, downloadLogFile } from '../components/utils/logs'
import LogViewer from '../components/LogViewer'
import DownloadButton from '../components/DownloadButton'
import LogFilters from '../components/LogFilters'
import ReloadButton from '../components/ReloadButton'
import BackToHomeButton from '../components/BackToHomeButton'
import Footer from '../components/Footer'

const LOG_FILE = 'ble_events.log'

const LogsPage = () => {
  const [logLines, setLogLines] = useState<string[]>([])
  const [error, setError] = useState<string | null>(null)
  const [selectedLevel, setSelectedLevel] = useState<'ALL' | 'INFO' | 'WARNING' | 'ERROR' | 'CRITICAL'>('ALL')

  const handleReload = () => {
    fetchLogFile(LOG_FILE)
      .then(setLogLines)
      .catch(() => setError('❌ Error al cargar el archivo de logs'))
  }

  useEffect(() => {
    handleReload()
  }, [])

  return (
    <div className="bg-gray-950 min-h-screen w-screen flex flex-col font-inter text-gray-100">
      <main className="flex-1 overflow-y-auto px-4 sm:px-8 py-8 flex flex-col items-center space-y-8">

        {/* Título con fondo animado */}
        <div className="relative w-full">
          <h2 className="text-center text-3xl sm:text-4xl md:text-5xl font-extrabold text-cyan-400 drop-shadow-lg animate-pulse">
            📜 Monitor de eventos BLE (logs)
          </h2>
          <p className="text-center text-sm text-gray-400 mt-1">
            Visualiza, filtra y descarga los eventos recientes registrados por el sistema IoT BLE.
          </p>
          <div className="absolute top-0 right-0">
            <BackToHomeButton />
          </div>
        </div>

        {/* Filtro por nivel */}
        <section className="w-full max-w-4xl">
          <LogFilters selectedLevel={selectedLevel} onSelectLevel={setSelectedLevel} />
        </section>

        {/* Acciones: Recargar / Descargar */}
        <div className="flex gap-4 flex-wrap justify-center">
          <DownloadButton onClick={() => downloadLogFile(LOG_FILE, logLines)} />
          <ReloadButton onClick={handleReload} />
        </div>

        {/* Visor de logs centrado */}
        <section className="w-full flex justify-center">
          <div className="w-full max-w-4xl">
            <LogViewer lines={logLines} error={error} selectedLevel={selectedLevel} />
          </div>
        </section>
        {/* 📄 Footer - Pie de página*/}
        <Footer />
      </main>
    </div>
  )
}

export default LogsPage
