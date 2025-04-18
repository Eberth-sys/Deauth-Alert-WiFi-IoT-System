//frontend\src\components\AlertHeatmapTable.tsx
import { useEffect, useRef, useState } from 'react'
import AlertSummaryTable from './AlertSummaryTable'
import NodeStatusTable from './NodeStatusTable'
import { AlertSummary, NodeStatus, AggregatedAlert } from './types'
import { connectToWebSocket } from '../services/socket'

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
  const socketRef = useRef<WebSocket | null>(null)
  const [connectionStatus, setConnectionStatus] = useState<'connected' | 'disconnected' | 'reconnecting'>('disconnected')

  useEffect(() => {
    let isMounted = true

    const fetchResumen = async () => {
      try {
        const res = await fetch('http://192.168.255.132:8000/alerts-summary')
        const data = await res.json()
        if (isMounted) setAlertSummary(data)
      } catch (err) {
        console.error('Error al obtener resumen de alertas:', err)
      }
    }

    const fetchStatus = async () => {
      try {
        const res = await fetch('http://192.168.255.132:8000/esp32-nodes')
        const data = await res.json()
        if (isMounted) setNodeStatus(data)
      } catch (err) {
        console.error('Error al obtener estado de nodos:', err)
      }
    }

    fetchResumen()
    fetchStatus()

    const socket = connectToWebSocket(
      () => {
        fetchResumen()
        fetchStatus()
      },
      () => setConnectionStatus('disconnected'),
      setConnectionStatus
    )

    socketRef.current = socket

    return () => {
      isMounted = false
      socketRef.current?.close()
    }
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

  const getConnectionIndicator = () => {
    switch (connectionStatus) {
      case 'connected':
        return <span className="text-green-400 font-semibold animate-pulse">🟢 Conectado en Tiempo Real</span>
      case 'reconnecting':
        return <span className="text-yellow-400 font-semibold animate-pulse">🟡 Reconectando...</span>
      case 'disconnected':
      default:
        return <span className="text-red-400 font-semibold">🔴 Sin Conexión</span>
    }
  }

  return (
    <div className="w-full px-4 md:px-8 py-6 space-y-10 font-inter">
      {/* TÍTULO PRINCIPAL */}
      <div className="text-center">
        <p className="text-gray-400 mt-1 text-sm sm:text-base">
          Sistema en tiempo real para detección de ataques de desautenticación sobre redes WiFi.
        </p>
      </div>

      {/* ESTADO DE CONEXIÓN */}
      <div className="text-center">
        <div className="inline-block px-4 py-2 rounded-full bg-gray-800 border border-gray-600 shadow text-sm">
          {getConnectionIndicator()}
        </div>
      </div>

      {/* TABLA DE ALERTAS */}
      <section className="space-y-2">
        <h2 className="text-lg sm:text-xl font-semibold text-purple-400">📊 Resumen de Actividad por Canal</h2>
        <AlertSummaryTable data={data} />
      </section>

      {/* TABLA DE ESTADO DE NODOS */}
      <section className="space-y-2">
        <h2 className="text-lg sm:text-xl font-semibold text-emerald-400">💡 Estado Actual de Nodos IoT</h2>
        <NodeStatusTable status={nodeStatus} />
      </section>
    </div>
  )
}

export default AlertHeatmapTable
