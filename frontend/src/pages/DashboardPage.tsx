//frontend\src\pages\DashboardPage.tsx

// -------------------- Importaciones --------------------
import { useEffect, useRef, useState } from 'react'
import AlertSummaryTable from '../components/AlertSummaryTable'
import NodeStatusTable from '../components/NodeStatusTable'
import AlertNotification from '../components/AlertNotification'
import ConnectionNotification from '../components/ConnectionNotification'
import { AlertSummary, AggregatedAlert, NodeStatus } from '../components/types'
import { connectToWebSocket } from '../services/socket'
import { useAlertWatcher } from '../hooks/useAlertWatcher'
import { useNodeConnectionWatcher } from '../hooks/useNodeConnectionWatcher'

// -------------------- URL base del backend --------------------
const API_URL = import.meta.env.VITE_BACKEND_URL || "http://localhost:8000"

// -------------------- Declaración de nodos esperados --------------------
const NODOS_ESPERADOS: { nodo_iot: string; canal: number }[] = [
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

// -------------------- Componente principal --------------------
const DashboardPage = () => {
  const [alertSummary, setAlertSummary] = useState<AlertSummary[]>([])
  const [nodeStatus, setNodeStatus] = useState<NodeStatus[]>([])
  const [connectionStatus, setConnectionStatus] = useState<'connected' | 'disconnected' | 'reconnecting'>('disconnected')
  const socketRef = useRef<WebSocket | null>(null)

  const { alertMessage, checkAlertThreshold } = useAlertWatcher()
  const { connectionAlert, checkConnectionChanges, setConnectionAlert } = useNodeConnectionWatcher()

  // 🧠 Fusiona datos de alertas y estado para la tabla
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

  // 🔴🟢 Muestra estado visual del WebSocket
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

  // 🛰️ Fetch inicial y conexión WebSocket
  useEffect(() => {
    let isMounted = true

    // Consulta alertas por canal
    const fetchResumen = async () => {
      try {
        const res = await fetch(`${API_URL}/alerts-summary`)
        const data = await res.json()
        if (isMounted) {
          setAlertSummary(data)
          checkAlertThreshold(data)
        }
      } catch (err) {
        console.error('Error al obtener resumen de alertas:', err)
      }
    }

    // Consulta estado de nodos ESP32
    const fetchStatus = async () => {
      try {
        const res = await fetch(`${API_URL}/esp32-nodes`)
        const data = await res.json()
        if (isMounted) {
          setNodeStatus(data)
          checkConnectionChanges(data)
        }
      } catch (err) {
        console.error('Error al obtener estado de nodos:', err)
      }
    }

    // Carga inicial
    fetchResumen()
    fetchStatus()

    // Establece WebSocket
    const socket = connectToWebSocket(
      () => {
        fetchResumen()
        fetchStatus()
      },
      () => setConnectionStatus('disconnected'),
      setConnectionStatus
    )

    socketRef.current = socket

    // Limpieza al desmontar
    return () => {
      isMounted = false
      socketRef.current?.close()
    }
  }, [])

  const data = aggregateAlerts()

  return (
    <div className="w-full px-4 md:px-8 py-6 space-y-10 font-inter">
      {/* 🔔 Alertas por seguridad o conexión */}
      {alertMessage && (
        <AlertNotification message={alertMessage} onClose={() => {}} sound="/sounds/warning.mp3" />
      )}
      {connectionAlert && (
        <ConnectionNotification message={connectionAlert} onClose={() => setConnectionAlert(null)} />
      )}

      {/* 💬 Introducción y estado de conexión */}
      <div className="text-center">
        <p className="text-gray-400 mt-1 text-sm sm:text-base">
          Sistema en tiempo real para detección de ataques de desautenticación sobre redes WiFi.
        </p>
      </div>
      <div className="text-center">
        <div className="inline-block px-4 py-2 rounded-full bg-gray-800 border border-gray-600 shadow text-sm">
          {getConnectionIndicator()}
        </div>
      </div>

      {/* 📊 Tablas con datos de actividad y nodos */}
      <section className="space-y-2">
        <h2 className="text-lg sm:text-xl font-semibold text-purple-400">📊 Resumen de actividad por canal</h2>
        <AlertSummaryTable data={data} />
      </section>

      <section className="space-y-2">
        <h2 className="text-lg sm:text-xl font-semibold text-emerald-400">💡 Estado actual de nodos IoT</h2>
        <NodeStatusTable status={nodeStatus} />
      </section>
    </div>
  )
}

export default DashboardPage
