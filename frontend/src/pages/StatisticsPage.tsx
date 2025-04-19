import { useEffect, useState } from 'react'
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

const StatisticsPage = () => {
  const [total, setTotal] = useState(0)
  const [porNodo, setPorNodo] = useState([])
  const [porCanal, setPorCanal] = useState([])
  const [ultimas, setUltimas] = useState([])

  useEffect(() => {
    fetchTotalAlerts().then((res) => setTotal(res.total_alertas))
    fetchAlertsByNode().then(setPorNodo)
    fetchAlertsByChannel().then(setPorCanal)
    fetchLatestAlerts().then(setUltimas)
  }, [])

  return (
    <div className="bg-gray-900 min-h-screen w-screen flex flex-col font-inter text-gray-100">
      <main className="flex-1 overflow-y-auto px-4 sm:px-8 py-8 flex flex-col items-center">
        <div className="w-full max-w-screen-xl space-y-10">

          {/* Título con botón de regreso */}
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

          {/* Últimas alertas en bloque separado */}
          <section className="rounded-xl bg-gray-800/80 p-4 shadow-lg ring-1 ring-gray-700">
            <LatestAlertsTable alerts={ultimas} />
          </section>
        </div>
      </main>
    </div>
  )
}

export default StatisticsPage
