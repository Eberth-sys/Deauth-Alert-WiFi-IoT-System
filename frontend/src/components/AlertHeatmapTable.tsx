//frontend\src\components\AlertHeatmapTable.tsx

import { useEffect, useState } from 'react'

// Componentes
import TableHeader from './TableHeader'
import AlertRow from './AlertRow'

// Tipos y utilidades
import { AlertSummary, NodeStatus, AggregatedAlert } from './types'
import {
  getAlertIndicatorColor,
  getAlertIndicatorText,
  getConnectionStatusStyle,
  getConnectionStatusText,
  getHeatColor,
  formatDate,
} from './utils/formatters'

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
        lastSeen: summary?.last_seen || '-',
        spoofed_bssid: summary?.spoofed_bssid || '-',
        target_mac: summary?.target_mac || '-',
        isConnected: status?.status === 'connected',
        lastConnection: status?.last_update || '-',
      }
    })
  }

  const data = aggregateAlerts()

  return (
    <div className="w-full px-4">
      <h2 className="text-xl font-bold text-center text-gray-100 mb-4 leading-tight">
        Alertas por Nodo IoT
      </h2>

      <div className="overflow-x-auto shadow-2xl rounded-lg">
        <table className="w-full table-auto bg-gray-800 text-gray-100 text-sm leading-tight">
          <TableHeader />
          <tbody>
            {data.map((row, idx) => (
              <AlertRow
                key={idx}
                index={idx}
                {...row}
              />
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default AlertHeatmapTable
