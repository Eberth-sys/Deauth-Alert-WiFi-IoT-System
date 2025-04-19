import React, { useEffect } from 'react'

// Definición de los props esperados
interface AlertNotificationProps {
  message: string                  // Mensaje a mostrar en la alerta
  onClose: () => void              // Función que cierra la alerta
  duration?: number                // Duración visible de la alerta (por defecto 10s)
}

// Componente de alerta visual y sonora
const AlertNotification: React.FC<AlertNotificationProps> = ({
  message,
  onClose,
  duration = 10000 // 10 segundos por defecto
}) => {
  useEffect(() => {
    //  Reproduce un sonido al disparar la alerta
    const audio = new Audio('/sounds/warning.mp3') // Ruta relativa desde public/
    audio.play().catch((e) => console.warn('🔇 No se pudo reproducir el sonido:', e))

    //  Oculta la alerta automáticamente después del tiempo indicado
    const timeout = setTimeout(() => {
      onClose()
    }, duration)

    // Limpieza al desmontar el componente
    return () => clearTimeout(timeout)
  }, [onClose, duration])

  return (
    <div className="fixed top-6 left-1/2 transform -translate-x-1/2 z-50 px-6 py-4 rounded-2xl shadow-2xl backdrop-blur-md border border-red-400 ring-1 ring-red-500/40 bg-gradient-to-r from-red-600 to-pink-600 text-white font-semibold text-sm sm:text-base flex items-center gap-3 animate-fadeIn">
      {/* Ícono con animación sutil */}
      <span className="text-xl animate-ping-slow">⚠️</span>
      <span>
        <strong>Alerta de Seguridad:</strong> {message}
      </span>
    </div>
  )
}

export default AlertNotification
