// frontend/src/components/AlertNotification.tsx

import React, { useEffect } from 'react'

// Definimos las props que acepta este componente de notificación
interface AlertNotificationProps {
  message: string            // Mensaje que se mostrará en la alerta
  onClose: () => void        // Función que se ejecuta al cerrar la alerta
  duration?: number          // Duración en milisegundos antes de ocultar la alerta automáticamente
}

// Componente que muestra una alerta visual en pantalla con temporizador
const AlertNotification: React.FC<AlertNotificationProps> = ({
  message,
  onClose,
  duration = 10000 // Valor por defecto: 10 segundos
}) => {
  // Efecto que se dispara al montar el componente para iniciar el temporizador
  useEffect(() => {
    const timeout = setTimeout(() => {
      onClose() // Cierra la alerta cuando pasa el tiempo
    }, duration)

    // Limpieza del temporizador al desmontar el componente
    return () => clearTimeout(timeout)
  }, [onClose, duration])

  return (
    // Estilo visual centrado y destacado para la alerta
    <div className="fixed top-5 left-1/2 transform -translate-x-1/2 z-50 bg-red-600 text-white px-6 py-3 rounded-full shadow-lg text-sm sm:text-base font-semibold animate-pulse border border-white backdrop-blur-md">
      ⚠️ Alerta de Seguridad: {message}
    </div>
  )
}

export default AlertNotification
