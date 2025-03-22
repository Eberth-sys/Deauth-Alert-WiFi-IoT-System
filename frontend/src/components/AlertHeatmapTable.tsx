// frontend/src/components/AlertHeatmapTable.tsx

type AlertEvent = {
  nodo_iot: string
  spoofed_bssid: string
  target_mac: string
  bssid: string
  canal: number
  id: number
  timestamp: string
}

type AggregatedAlert = {
  nodo_iot: string
  canal: number
  count: number
  lastSeen: string
  spoofed_bssid: string
  target_mac: string
  isConnected: boolean
}

const mockData: AlertEvent[] = [
  {
    nodo_iot: 'ESP32_2_CH_06',
    spoofed_bssid: 'REDACTED_BSSID',
    target_mac: 'REDACTED_BSSID',
    bssid: 'FF:FF:FF:FF:FF:FF',
    canal: 6,
    id: 9,
    timestamp: '2025-03-09T21:56:40.101760',
  },
  {
    nodo_iot: 'ESP32_2_CH_06',
    spoofed_bssid: 'REDACTED_BSSID',
    target_mac: 'REDACTED_BSSID',
    bssid: 'FF:FF:FF:FF:FF:FF',
    canal: 6,
    id: 8,
    timestamp: '2025-03-09T21:56:38.101760',
  },
  {
    nodo_iot: 'ESP32_4_SCANN',
    spoofed_bssid: 'AA:BB:CC:DD:EE:FF',
    target_mac: 'AA:BB:CC:DD:EE:FF',
    bssid: 'FF:FF:FF:FF:FF:FF',
    canal: 7,
    id: 7,
    timestamp: '2025-03-09T21:56:39.101760',
  },
]

const aggregateAlerts = (data: AlertEvent[]): AggregatedAlert[] => {
  const grouped: Record<string, AggregatedAlert> = {}
  let i = 0

  for (const event of data) {
    const key = `${event.nodo_iot}_${event.canal}`
    if (!grouped[key]) {
      grouped[key] = {
        nodo_iot: event.nodo_iot,
        canal: event.canal,
        count: 1,
        lastSeen: event.timestamp,
        spoofed_bssid: event.spoofed_bssid,
        target_mac: event.target_mac,
        // Simulación de estado de conexión
        isConnected: i % 2 === 0,
      }
    } else {
      grouped[key].count += 1
      if (event.timestamp > grouped[key].lastSeen) {
        grouped[key].lastSeen = event.timestamp
      }
    }
    i++
  }

  return Object.values(grouped)
}

const getHeatColor = (count: number) => {
  if (count >= 100) return 'bg-red-600 text-white'
  if (count >= 50) return 'bg-orange-500 text-white'
  if (count >= 10) return 'bg-yellow-400 text-black'
  return 'bg-green-400 text-black'
}

const getConnectionStatusStyle = (isConnected: boolean) => {
  return isConnected ? 'text-green-400' : 'text-red-400'
}
const getConnectionStatusText = (isConnected: boolean) => {
  return isConnected ? 'Conectado' : 'Desconectado'
}

const getAlertIndicatorColor = (count: number) => {
  return count > 0 ? 'bg-red-500' : 'bg-green-500'
}
const getAlertIndicatorText = (count: number) => {
  return count > 0 ? 'Alerta' : 'Ok'
}

const AlertHeatmapTable = () => {
  const data = aggregateAlerts(mockData)

  return (
    <div className="w-full px-4">
      <h2 className="text-xl font-bold text-center text-gray-100 mb-4 leading-tight">
        Alertas por Nodo IoT
      </h2>

      <div className="overflow-x-auto shadow-2xl rounded-lg">
        {/* 
          text-sm => fuente más pequeña
          leading-tight => reduce el interlineado
        */}
        <table className="w-full table-auto text-xs text-gray-100 leading-snug bg-gray-800 shadow-md rounded-md">
          <thead className="bg-gradient-to-r from-blue-600 to-blue-400 text-white uppercase tracking-wider">
            <tr>
              <th className="px-3 py-2 text-left">Nodo IoT</th>
              <th className="px-3 py-2 text-left">Canal</th>
              <th className="px-3 py-2 text-center">Nº Alertas</th>
              <th className="px-3 py-2 text-left">Última Alerta</th>
              <th className="px-3 py-2 text-left">BSSID Suplantado</th>
              <th className="px-3 py-2 text-left">MAC Objetivo</th>
              <th className="px-3 py-2 text-left">Estado del Nodo</th>
              <th className="px-3 py-2 text-left">Indicador de Alerta</th>
            </tr>
          </thead>
          <tbody>
            {data.map((row, idx) => (
              <tr
                key={idx}
                className={`
                  ${idx % 2 === 0 ? 'bg-gray-600' : 'bg-gray-800'}
                  hover:bg-gray-600 transition-colors duration-200
                `}
              >
                <td className="px-3 py-2 border-b border-gray-700">
                  {row.nodo_iot}
                </td>
                <td className="px-3 py-2 border-b border-gray-700">
                  {row.canal}
                </td>
                <td
                  className={`
                    px-3 py-2 border-b border-gray-700 font-bold text-center
                    ${getHeatColor(row.count)}
                  `}
                >
                  {row.count}
                </td>
                <td className="px-3 py-2 border-b border-gray-700">
                  {new Date(row.lastSeen).toLocaleString()}
                </td>
                <td className="px-3 py-2 border-b border-gray-700">
                  {row.spoofed_bssid}
                </td>
                <td className="px-3 py-2 border-b border-gray-700">
                  {row.target_mac}
                </td>
                <td className="px-3 py-2 border-b border-gray-700">
                  <span className={getConnectionStatusStyle(row.isConnected)}>
                    {getConnectionStatusText(row.isConnected)}
                  </span>
                </td>
                <td className="px-3 py-2 border-b border-gray-700">
                  <div className="flex items-center">
                    <div
                      className={`w-3 h-3 rounded-full mr-2 ${getAlertIndicatorColor(
                        row.count
                      )}`}
                    />
                    <span>{getAlertIndicatorText(row.count)}</span>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default AlertHeatmapTable
