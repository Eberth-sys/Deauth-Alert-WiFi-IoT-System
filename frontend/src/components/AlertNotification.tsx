import React, { useEffect } from 'react'

// Props que acepta el componente de alerta
interface AlertNotificationProps {
  message: string                // Texto de la alerta
  onClose: () => void            // Función para cerrar la alerta
  duration?: number              // Tiempo visible (por defecto 10s)
  sound?: string                 // Ruta del sonido opcional
}

// Componente de alerta visual y sonora
const AlertNotification: React.FC<AlertNotificationProps> = ({
  message,
  onClose,
  duration = 10000,
  sound = '/sounds/warning.mp3' // Valor por defecto si no se pasa otro sonido
}) => {
  useEffect(() => {
    const audio = new Audio(sound)
    audio.play().catch((e) => console.warn('🔇 No se pudo reproducir el sonido:', e))

    const timeout = setTimeout(() => {
      onClose()
    }, duration)

    return () => clearTimeout(timeout)
  }, [onClose, duration, sound])

  return (
    <div className="fixed top-6 left-1/2 transform -translate-x-1/2 z-50 px-6 py-4 rounded-2xl shadow-2xl backdrop-blur-md border border-red-400 ring-1 ring-red-500/40 bg-gradient-to-r from-red-600 to-pink-600 text-white font-semibold text-sm sm:text-base flex items-center gap-3 animate-fadeIn">
      <span className="text-xl animate-ping-slow">⚠️</span>
      <span>
        <strong>Alerta de Seguridad:</strong> {message}
      </span>
    </div>
  )
}

export default AlertNotification
