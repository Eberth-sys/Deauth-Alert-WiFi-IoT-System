// frontend/src/hooks/useAlertWatcher.ts

import { useRef, useState } from 'react'
import { AlertSummary } from '../components/types'

// Umbral mínimo de alertas para disparar una notificación
const UMBRAL = 3

// Hook personalizado que monitorea si algún nodo IoT aumenta su número de alertas
export const useAlertWatcher = () => {
  // Estado que contiene el mensaje de alerta activa (si hay alguna)
  const [alertMessage, setAlertMessage] = useState<string | null>(null)

  // Referencia a los valores anteriores del resumen de alertas (para comparar con los nuevos)
  const prevSummaryRef = useRef<AlertSummary[]>([])

  // Función que compara los valores actuales con los anteriores para detectar cambios
  const checkAlertThreshold = (newSummary: AlertSummary[]) => {
    const prevSummary = prevSummaryRef.current

    //  Si es la primera vez que se ejecuta, solo se guardan los datos, no se compara nada
    if (prevSummary.length === 0) {
      prevSummaryRef.current = newSummary
      return
    }

    //  Si todos los nodos tienen 0 alertas, reiniciamos el comparador
    const allZero = newSummary.every((n) => n.count === 0)
    if (allZero) {
      prevSummaryRef.current = []
      return
    }

    //  Comparación: buscamos si algún nodo ha incrementado su número de alertas
    for (const nuevo of newSummary) {
      const anterior = prevSummary.find((n) => n.canal === nuevo.canal)
      const anteriorCount = anterior?.count ?? 0

      if (nuevo.count > anteriorCount && nuevo.count > UMBRAL) {
        //  Si hay un aumento que supera el umbral, se dispara una alerta
        setAlertMessage(`El nodo ${nuevo.nodo_iot} ha recibido ${nuevo.count} alertas.`)

        //  La alerta se cierra automáticamente después de 10 segundos
        setTimeout(() => setAlertMessage(null), 10000)
        break //  Opcional: evitamos múltiples alertas simultáneas
      }
    }

    // Guardamos la nueva data para la próxima comparación
    prevSummaryRef.current = newSummary
  }

  // Retornamos la alerta activa y la función para evaluar nuevos datos
  return {
    alertMessage,
    checkAlertThreshold
  }
}
