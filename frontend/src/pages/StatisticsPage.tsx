//frontend\src\pages\StatisticsPage.tsx

// Hooks y servicios necesarios
import { useEffect, useRef, useState } from 'react'

// Servicios que consultan estadísticas al backend
import {
  fetchAlertsByChannel,
  fetchAlertsByNode,
  fetchLatestAlerts,
  fetchTotalAlerts
} from '../services/stats'

// Componentes visuales del dashboard
import StatsCard from '../components/StatsCard'
import StatsTable from '../components/StatsTable'
import LatestAlertsTable from '../components/LatestAlertsTable'
import BackToHomeButton from '../components/BackToHomeButton'
import { connectToWebSocket } from '../services/socket'
import Footer from '../components/Footer'
import type { AlertEvent } from '../components/types'

// Componente principal del panel de estadísticas
const StatisticsPage = () => {
  // Estados para guardar los datos estadísticos obtenidos
  const [total, setTotal] = useState(0)
  const [porNodo, setPorNodo] = useState([])
  const [porCanal, setPorCanal] = useState([])
  const [ultimas, setUltimas] = useState<AlertEvent[]>([])

  // Estado para mostrar si el WebSocket está activo
  const [connectionStatus, setConnectionStatus] = useState<'connected' | 'disconnected' | 'reconnecting'>('disconnected')
  const socketRef = useRef<WebSocket | null>(null)

  // Función central para cargar todos los datos estadísticos
  const fetchAll = () => {
    fetchTotalAlerts().then((res) => setTotal(res.total_alertas))
    fetchAlertsByNode().then(setPorNodo)
    fetchAlertsByChannel().then(setPorCanal)
    fetchLatestAlerts().then(setUltimas)
  }

  // Se ejecuta al montar el componente: conecta al WebSocket y carga datos
  useEffect(() => {
    fetchAll()

    const socket = connectToWebSocket(
      () => fetchAll(), // Se vuelve a cargar todo cuando hay cambios
      () => setConnectionStatus('disconnected'), // Manejo de error
      setConnectionStatus // Actualiza el estado visual del socket
    )

    socketRef.current = socket

    return () => {
      socketRef.current?.close()
    }
  }, [])

  // Muestra un indicador visual según el estado de conexión del WebSocket
  const getConnectionIndicator = () => {
    switch (connectionStatus) {
      case 'connected':
        return <span className="text-green-400 font-semibold animate-pulse">🟢 Conectado en tiempo real</span>
      case 'reconnecting':
        return <span className="text-yellow-400 font-semibold animate-pulse">🟡 Reconectando...</span>
      default:
        return <span className="text-red-400 font-semibold">🔴 Sin conexión</span>
    }
  }

  return (
    <div className="bg-gray-900 h-screen w-screen flex flex-col font-inter text-gray-100">
      <main className="flex-1 overflow-y-auto px-4 sm:px-8 py-8 flex flex-col items-center">

        {/* Contenedor principal de ancho limitado */}
        <div className="w-full max-w-screen-xl space-y-10">

          {/* Encabezado del panel con botón de regreso */}
          <div className="relative text-center mb-2">
            <h2 className="text-3xl sm:text-4xl md:text-5xl font-extrabold text-blue-400 drop-shadow-md">
              📈 Panel de estadísticas de alertas
            </h2>
            <p className="text-sm text-gray-400 mt-2">
              Visualiza el comportamiento reciente y acumulado de amenazas detectadas por los nodos IoT.
            </p>
            <div className="absolute top-0 right-0">
              <BackToHomeButton />
            </div>
          </div>

          {/* Indicador del estado del WebSocket */}
          <div className="text-center">
            <div className="inline-block px-4 py-2 rounded-full bg-gray-800 border border-gray-600 shadow text-sm">
              {getConnectionIndicator()}
            </div>
          </div>

          {/* Tarjeta con el total de alertas registradas */}
          <div className="flex justify-end mb-6">
            <div className="w-full sm:w-auto">
              <StatsCard label="Total de alertas" value={total} icon="🚨" color="bg-red-600" />
            </div>
          </div>

          {/* Dos tablas: una por nodo IoT y otra por canal */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="rounded-xl bg-gray-800/80 p-4 shadow-md ring-1 ring-gray-700">
              <StatsTable
                title="📊 Alertas por nodo IoT"
                headers={['nodo_iot', 'total_alertas']}
                data={porNodo}
              />
            </div>
            <div className="rounded-xl bg-gray-800/80 p-4 shadow-md ring-1 ring-gray-700">
              <StatsTable
                title="📡 Canales más afectados"
                headers={['canal', 'total_alertas']}
                data={porCanal}
              />
            </div>
          </div>

          {/* Tabla con las últimas 10 alertas registradas */}
          <section className="rounded-xl bg-gray-800/80 p-4 shadow-lg ring-1 ring-gray-700">
            <LatestAlertsTable alerts={ultimas} />
          </section>
        </div>
        {/* 📄 Footer - Pie de página*/}
        <Footer />
      </main>
    </div>
  )
}

export default StatisticsPage
