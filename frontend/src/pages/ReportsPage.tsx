//frontend\src\pages\ReportsPage.tsx

import { useState } from 'react'
import { fetchAlertsByDate, fetchAlertsToday } from '../services/reports'
import ReportsTable from '../components/ReportsTable'

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
    try {
      const data = await fetchAlertsByDate(startDate, endDate)
      setAlerts(data)
      setError('')
    } catch {
      setError('❌ Error al consultar el rango de fechas')
    }
  }

  const handleTodayQuery = async () => {
    try {
      const data = await fetchAlertsToday()
      setAlerts(data)
      setError('')
    } catch {
      setError('❌ Error al consultar alertas de hoy')
    }
  }

  return (
    <div className="bg-gray-900 h-screen w-screen flex flex-col">
      <main className="flex-1 overflow-y-auto px-4 py-8 flex flex-col items-center">
        <div className="relative w-full max-w-screen-xl">
          <h2 className="text-5xl font-extrabold text-blue-400 text-center mb-6 animate-pulse drop-shadow-[0_0_10px_rgba(59,130,246,0.7)]">
            📅 Reportes Personalizados
          </h2>

          {/* Filtros */}
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

          {/* Error */}
          {error && <p className="text-red-400 text-center mb-4">{error}</p>}

          {/* Tabla */}
          <ReportsTable alerts={alerts} />
        </div>
      </main>
    </div>
  )
}

export default ReportsPage
