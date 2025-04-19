//frontend\src\pages\DashboardPage.tsx

// Importa las tablas de resumen y estado
import AlertSummaryTable from '../components/AlertSummaryTable'
import NodeStatusTable from '../components/NodeStatusTable'

// Hooks y tipos necesarios
import { useEffect, useRef, useState } from 'react'
import { AlertSummary, NodeStatus, AggregatedAlert } from '../components/types'
import { connectToWebSocket } from '../services/socket'

// Lista fija de nodos y canales esperados en el sistema
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

const DashboardPage = () => {
  // Estados para guardar datos de resumen y nodos
  const [alertSummary, setAlertSummary] = useState<AlertSummary[]>([])
  const [nodeStatus, setNodeStatus] = useState<NodeStatus[]>([])

  // Referencia al WebSocket para manejo de reconexiones
  const socketRef = useRef<WebSocket | null>(null)

  // Estado para saber si el WebSocket está activo
  const [connectionStatus, setConnectionStatus] = useState<'connected' | 'disconnected' | 'reconnecting'>('disconnected')

  // Hook que se ejecuta al montar el componente
  useEffect(() => {
    let isMounted = true

    // Carga resumen de alertas desde el backend
    const fetchResumen = async () => {
      try {
        const res = await fetch('http://192.168.255.132:8000/alerts-summary')
        const data = await res.json()
        if (isMounted) setAlertSummary(data)
      } catch (err) {
        console.error('Error al obtener resumen de alertas:', err)
      }
    }

    // Carga estado de los nodos desde el backend
    const fetchStatus = async () => {
      try {
        const res = await fetch('http://192.168.255.132:8000/esp32-nodes')
        const data = await res.json()
        if (isMounted) setNodeStatus(data)
      } catch (err) {
        console.error('Error al obtener estado de nodos:', err)
      }
    }

    // Ejecuta las dos consultas al iniciar
    fetchResumen()
    fetchStatus()

    // Conecta al WebSocket y actualiza datos en tiempo real
    const socket = connectToWebSocket(
      () => {
        fetchResumen()
        fetchStatus()
      },
      () => setConnectionStatus('disconnected'),
      setConnectionStatus
    )

    socketRef.current = socket

    // Cleanup: cierra conexión si el componente se desmonta
    return () => {
      isMounted = false
      socketRef.current?.close()
    }
  }, [])

  // Combina datos de resumen y estado con la lista esperada de nodos
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

  // Resultado final con los datos combinados
  const data = aggregateAlerts()

  // Indicador visual del estado de conexión WebSocket
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
    <div className="w-full px-4 md:px-8 py-6 space-y-10 font-inter">
      
      {/* Descripción inicial */}
      <div className="text-center">
        <p className="text-gray-400 mt-1 text-sm sm:text-base">
          Sistema en tiempo real para detección de ataques de desautenticación sobre redes WiFi.
        </p>
      </div>

      {/* Indicador de conexión */}
      <div className="text-center">
        <div className="inline-block px-4 py-2 rounded-full bg-gray-800 border border-gray-600 shadow text-sm">
          {getConnectionIndicator()}
        </div>
      </div>

      {/* Sección de resumen de actividad */}
      <section className="space-y-2">
        <h2 className="text-lg sm:text-xl font-semibold text-purple-400">📊 Resumen de Actividad por Canal</h2>
        <AlertSummaryTable data={data} />
      </section>

      {/* Sección de estado de nodos */}
      <section className="space-y-2">
        <h2 className="text-lg sm:text-xl font-semibold text-emerald-400">💡 Estado Actual de Nodos IoT</h2>
        <NodeStatusTable status={nodeStatus} />
      </section>
    </div>
  )
}

export default DashboardPage
