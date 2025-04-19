//frontend\src\pages\StatisticsPage.tsx

import { useEffect, useRef, useState } from 'react'
import {
  fetchAlertsByChannel,
  fetchAlertsByNode,
  fetchLatestAlerts,
  fetchTotalAlerts
} from '../services/stats'
import StatsCard from '../components/StatsCard'
import StatsTable from '../components/StatsTable'
import LatestAlertsTable from '../components/LatestAlertsTable'
import BackToHomeButton from '../components/BackToHomeButton'
import { connectToWebSocket } from '../services/socket'

const StatisticsPage = () => {
  const [total, setTotal] = useState(0)
  const [porNodo, setPorNodo] = useState([])
  const [porCanal, setPorCanal] = useState([])
  const [ultimas, setUltimas] = useState([])
  const [connectionStatus, setConnectionStatus] = useState<'connected' | 'disconnected' | 'reconnecting'>('disconnected')
  const socketRef = useRef<WebSocket | null>(null)

  const fetchAll = () => {
    fetchTotalAlerts().then((res) => setTotal(res.total_alertas))
    fetchAlertsByNode().then(setPorNodo)
    fetchAlertsByChannel().then(setPorCanal)
    fetchLatestAlerts().then(setUltimas)
  }

  useEffect(() => {
    fetchAll()

    const socket = connectToWebSocket(
      () => fetchAll(),
      () => setConnectionStatus('disconnected'),
      setConnectionStatus
    )

    socketRef.current = socket

    return () => {
      socketRef.current?.close()
    }
  }, [])

  const getConnectionIndicator = () => {
    switch (connectionStatus) {
      case 'connected':
        return <span className="text-green-400 font-semibold animate-pulse">🟢 Conectado en Tiempo Real</span>
      case 'reconnecting':
        return <span className="text-yellow-400 font-semibold animate-pulse">🟡 Reconectando...</span>
      default:
        return <span className="text-red-400 font-semibold">🔴 Sin Conexión</span>
    }
  }

  return (
    <div className="bg-gray-900 h-screen w-screen flex flex-col font-inter text-gray-100">
      <main className="flex-1 overflow-y-auto px-4 sm:px-8 py-8 flex flex-col items-center">
        <div className="w-full max-w-screen-xl space-y-10">
          <div className="relative text-center mb-2">
            <h2 className="text-3xl sm:text-4xl md:text-5xl font-extrabold text-blue-400 drop-shadow-md">
              📈 Panel de Estadísticas de Alertas
            </h2>
            <p className="text-sm text-gray-400 mt-2">
              Visualiza el comportamiento reciente y acumulado de amenazas detectadas por los nodos IoT.
            </p>
            <div className="absolute top-0 right-0">
              <BackToHomeButton />
            </div>
          </div>

          {/* Estado de conexión */}
          <div className="text-center">
            <div className="inline-block px-4 py-2 rounded-full bg-gray-800 border border-gray-600 shadow text-sm">
              {getConnectionIndicator()}
            </div>
          </div>

          {/* Total de alertas */}
          <div className="flex justify-end mb-6">
            <div className="w-full sm:w-auto">
              <StatsCard label="Total de Alertas" value={total} icon="🚨" color="bg-red-600" />
            </div>
          </div>

          {/* Tablas comparativas */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="rounded-xl bg-gray-800/80 p-4 shadow-md ring-1 ring-gray-700">
              <StatsTable
                title="📊 Alertas por Nodo IoT"
                headers={['nodo_iot', 'total_alertas']}
                data={porNodo}
              />
            </div>
            <div className="rounded-xl bg-gray-800/80 p-4 shadow-md ring-1 ring-gray-700">
              <StatsTable
                title="📡 Canales más Afectados"
                headers={['canal', 'total_alertas']}
                data={porCanal}
              />
            </div>
          </div>

          {/* Últimas alertas */}
          <section className="rounded-xl bg-gray-800/80 p-4 shadow-lg ring-1 ring-gray-700">
            <LatestAlertsTable alerts={ultimas} />
          </section>
        </div>
      </main>
    </div>
  )
}

export default StatisticsPage
