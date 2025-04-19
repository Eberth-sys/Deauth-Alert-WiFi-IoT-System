// frontend/src/hooks/useNodeConnectionWatcher.ts

import { useRef, useState } from 'react'
import { NodeStatus } from '../components/types'

// Hook que monitorea cambios de conexión en nodos
export const useNodeConnectionWatcher = () => {
  const [connectionAlert, setConnectionAlert] = useState<string | null>(null)
  const prevStatusRef = useRef<NodeStatus[]>([])

  // Compara el nuevo estado de los nodos con el anterior
  const checkNodeStatusChanges = (currentStatus: NodeStatus[]) => {
    const previous = prevStatusRef.current

    if (previous.length === 0) {
      prevStatusRef.current = currentStatus
      return
    }

    currentStatus.forEach((nuevoNodo) => {
      const anterior = previous.find((n) => n.device_name === nuevoNodo.device_name)

      if (anterior && anterior.status !== nuevoNodo.status) {
        const mensaje =
          nuevoNodo.status === 'disconnected'
            ? `El nodo ${nuevoNodo.device_name} se ha desconectado.`
            : `✅ El nodo ${nuevoNodo.device_name} se ha reconectado.`

        setConnectionAlert(mensaje)

        setTimeout(() => setConnectionAlert(null), 10000)
      }
    })

    prevStatusRef.current = currentStatus
  }

  return {
    connectionAlert,
    setConnectionAlert, // ✅ Se expone para el cierre manual
    checkConnectionChanges: checkNodeStatusChanges // ✅ Alias más semántico
  }
}
