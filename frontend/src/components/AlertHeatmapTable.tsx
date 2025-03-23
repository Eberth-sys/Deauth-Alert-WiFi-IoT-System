import { useEffect, useState } from 'react'
import dayjs from 'dayjs'                                    //Importo nuevo formato de hora! 
import 'dayjs/locale/es'                                    // Idioma español
import localizedFormat from 'dayjs/plugin/localizedFormat'

dayjs.extend(localizedFormat)
dayjs.locale('es')                      // Establecer español como idioma

type AlertSummary = {
  canal: number
  count: number
  last_seen: string | null
  nodo_iot: string
  spoofed_bssid: string
  target_mac: string
}

type NodeStatus = {
  device_name: string
  mac_address: string
  status: 'connected' | 'disconnected'
  last_update: string
}

type AggregatedAlert = {
  nodo_iot: string
  canal: number
  count: number
  lastSeen: string
  spoofed_bssid: string
  target_mac: string
  isConnected: boolean
  lastConnection: string
}

const NODOS_ESPERADOS = [
  { nodo_iot: 'ESP32_1_CH_01', canal: 1 },
  { nodo_iot: 'ESP32_4_SCANN', canal: 2 },
  { nodo_iot: 'ESP32_4_SCANN', canal: 3 },
  { nodo_iot: 'ESP32_4_SCANN', canal: 4 },
  { nodo_iot: 'ESP32_4_SCANN', canal: 5 },
  { nodo_iot: 'ESP32_2_CH_06', canal: 6 },
  { nodo_iot: 'ESP32_4_SCANN', canal: 7 },
  { nodo_iot: 'ESP32_4_SCANN', canal: 8 },
  { nodo_iot: 'ESP32_4_SCANN', canal: 9 },
  { nodo_iot: 'ESP32_4_SCANN', canal: 10 },
  { nodo_iot: 'ESP32_3_CH_11', canal: 11 },
  { nodo_iot: 'ESP32_4_SCANN', canal: 12 },
  { nodo_iot: 'ESP32_4_SCANN', canal: 13 },
  { nodo_iot: 'ESP32_4_SCANN', canal: 14 },
]

const AlertHeatmapTable = () => {
  const [alertSummary, setAlertSummary] = useState<AlertSummary[]>([])
  const [nodeStatus, setNodeStatus] = useState<NodeStatus[]>([])

  useEffect(() => {
    const fetchResumen = async () => {
      try {
        const res = await fetch('http://192.168.255.128:8000/alerts-summary')
        const data = await res.json()
        setAlertSummary(data)
      } catch (err) {
        console.error('Error al obtener resumen de alertas:', err)
      }
    }

    const fetchStatus = async () => {
      try {
        const res = await fetch('http://192.168.255.128:8000/esp32-nodes')
        const data = await res.json()
        setNodeStatus(data)
      } catch (err) {
        console.error('Error al obtener estado de nodos:', err)
      }
    }

    fetchResumen()
    fetchStatus()
    const interval = setInterval(() => {
      fetchResumen()
      fetchStatus()
    }, 5000)

    return () => clearInterval(interval)
  }, [])

  const aggregateAlerts = (): AggregatedAlert[] => {
    return NODOS_ESPERADOS.map(({ nodo_iot, canal }) => {
      const summary = alertSummary.find((s) => s.canal === canal)
      const status = nodeStatus.find((s) => s.device_name === nodo_iot)

      return {
        nodo_iot,
        canal,
        count: summary?.count || 0,
        lastSeen:  summary?.last_seen || '-', // 
        spoofed_bssid: summary?.spoofed_bssid || '-',
        target_mac: summary?.target_mac || '-',
        isConnected: status?.status === 'connected',
        lastConnection: status?.last_update || '-',
      }
    })
  }

  const getHeatColor = (count: number) => {
    if (count >= 100) return 'bg-red-600 text-white'
    if (count >= 50) return 'bg-orange-500 text-white'
    if (count >= 10) return 'bg-yellow-400 text-black'
    return 'bg-green-400 text-black'
  }

  const getConnectionStatusStyle = (isConnected: boolean) =>
    isConnected ? 'text-green-400' : 'text-red-400'
  const getConnectionStatusText = (isConnected: boolean) =>
    isConnected ? 'Conectado' : 'Desconectado'
  const getAlertIndicatorColor = (count: number) =>
    count > 0 ? 'bg-red-500' : 'bg-green-500'
  const getAlertIndicatorText = (count: number) =>
    count > 0 ? 'Alerta' : 'Ok'

  const data = aggregateAlerts()

  return (
    <div className="w-full px-4">
      <h2 className="text-xl font-bold text-center text-gray-100 mb-4 leading-tight">
        Alertas por Nodo IoT
      </h2>

      <div className="overflow-x-auto shadow-2xl rounded-lg">
        <table className="w-full table-auto bg-gray-800 text-gray-100 text-sm leading-tight">
          <thead className="bg-gradient-to-r from-blue-600 to-blue-400 text-white uppercase tracking-wider">
            <tr>
              <th className="px-2 py-1 text-left">Nodo IoT</th>
              <th className="px-2 py-1 text-left">Canal</th>
              <th className="px-2 py-1 text-center">Nº Alertas</th>
              <th className="px-2 py-1 text-left">Última Alerta</th>
              <th className="px-2 py-1 text-left">BSSID Suplantado</th>
              <th className="px-2 py-1 text-left">MAC Objetivo</th>
              <th className="px-2 py-1 text-left">Estado del Nodo</th>
              <th className="px-2 py-1 text-left">Indicador</th>
            </tr>
          </thead>
          <tbody>
            {data.map((row, idx) => (
              <tr
                key={idx}
                className={`${
                  idx % 2 === 0 ? 'bg-gray-700' : 'bg-gray-800'
                } hover:bg-gray-600 transition-all`}
              >
                <td className="px-2 py-1 border-b border-gray-700">
                  {row.nodo_iot}
                </td>
                <td className="px-2 py-1 border-b border-gray-700">
                  {row.canal}
                </td>
                <td
                  className={`px-2 py-1 border-b border-gray-700 font-bold text-center ${getHeatColor(row.count)}`}
                >
                  {row.count}
                </td>
                <td className="px-2 py-1 border-b border-gray-700">
                  {/* Formateo legible de fecha y hora larga para la columna "Última Alerta" */}
                  {row.lastSeen !== '-' ? dayjs(row.lastSeen).format('D [de] MMMM [de] YYYY, h:mm:ss A') : '-'}
                </td>
                <td className="px-2 py-1 border-b border-gray-700">
                  {row.spoofed_bssid}
                </td>
                <td className="px-2 py-1 border-b border-gray-700">
                  {row.target_mac}
                </td>
                <td className="px-2 py-1 border-b border-gray-700">
                  <span className={getConnectionStatusStyle(row.isConnected)}>
                    {getConnectionStatusText(row.isConnected)}
                  </span>
                </td>
                <td className="px-2 py-1 border-b border-gray-700">
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
