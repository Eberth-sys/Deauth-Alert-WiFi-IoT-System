//frontend\src\pages\ReportsPage.tsx

// Hooks y componentes necesarios
import { useState } from 'react'
import { fetchAlertsByDate, fetchAlertsToday } from '../services/reports'
import ReportsTable from '../components/ReportsTable'
import BackToHomeButton from '../components/BackToHomeButton'
import { downloadCSV } from '../components/utils/download'
import DownloadButton from '../components/DownloadButton' // reutilizamos el del LogsPage

// Definición del tipo de datos que representa una alerta
type AlertData = {
  id: number
  nodo_iot: string
  spoofed_bssid: string
  target_mac: string
  bssid: string
  canal: number
  timestamp: string
}

const ReportsPage = () => {
  const [alerts, setAlerts] = useState<AlertData[]>([])
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')
  const [error, setError] = useState('')

  const handleDateQuery = async () => {
    if (!startDate || !endDate) {
      setError('⚠️ Por favor selecciona una fecha de inicio y una de fin.')
      setTimeout(() => setError(''), 4000)
      return
    }

    try {
      const data = await fetchAlertsByDate(startDate, endDate)
      setAlerts(data)
      setError('')
    } catch {
      setError('❌ Error al consultar el rango de fechas')
      setTimeout(() => setError(''), 4000)
    }
  }

  const handleTodayQuery = async () => {
    try {
      const data = await fetchAlertsToday()
      setAlerts(data)
      setError('')
    } catch {
      setError('❌ Error al consultar alertas de hoy')
      setTimeout(() => setError(''), 4000)
    }
  }

  return (
    <div className="bg-gray-900 h-screen w-screen flex flex-col">
      <main className="flex-1 overflow-y-auto px-4 py-8 flex flex-col items-center">
        <div className="relative w-full max-w-screen-xl">
          <BackToHomeButton />
          <h2 className="text-5xl font-extrabold text-blue-400 text-center mb-6 animate-pulse drop-shadow-[0_0_10px_rgba(59,130,246,0.7)]">
            📅 Reportes Personalizados
          </h2>

          {/* Sección de filtros por fecha */}
          <div className="flex flex-col md:flex-row justify-center gap-4 mb-6">
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="bg-gray-800 border border-gray-600 rounded px-3 py-2 w-full md:w-auto"
            />
            <input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              className="bg-gray-800 border border-gray-600 rounded px-3 py-2 w-full md:w-auto"
            />
            <button
              onClick={handleDateQuery}
              className="bg-blue-500 hover:bg-blue-700 text-white font-semibold px-4 py-2 rounded w-full md:w-auto"
            >
              🔍 Consultar rango
            </button>
            <button
              onClick={handleTodayQuery}
              className="bg-emerald-500 hover:bg-emerald-700 text-white font-semibold px-4 py-2 rounded w-full md:w-auto"
            >
              📅 Hoy
            </button>
          </div>

          {/* Botón para exportar resultados a CSV */}
          {alerts.length > 0 && (
            <div className="flex justify-end mb-4">
              <DownloadButton onClick={() => downloadCSV(alerts, 'reporte_alertas')} />
            </div>
          )}

          {/* Mensaje de error */}
          {error && (
            <div className="text-center mb-4 animate-pulse">
              <div className="inline-block px-4 py-2 rounded bg-red-800 text-white shadow-lg border border-red-500 text-sm sm:text-base">
                {error}
              </div>
            </div>
          )}

          {/* Resultados de la consulta */}
          {alerts.length > 0 ? (
            <ReportsTable alerts={alerts} />
          ) : (
            <div className="text-center mt-6 text-gray-400 text-sm sm:text-base animate-fade-in">
              📭 No se encontraron alertas para el rango seleccionado.
            </div>
          )}
        </div>
      </main>
    </div>
  )
}

export default ReportsPage

