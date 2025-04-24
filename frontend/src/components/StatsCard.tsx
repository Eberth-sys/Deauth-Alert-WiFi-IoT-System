import { useEffect, useRef, useState } from 'react'

// Definición del tipo de props que recibe la tarjeta estadística
type Props = {
  label: string       // Texto descriptivo
  value: number       // Valor numérico que se muestra destacado
  icon?: string       // Icono decorativo opcional
  color?: string      // Clases Tailwind opcionales para personalizar el gradiente
}

// Componente funcional que representa una tarjeta visual de estadística
const StatsCard = ({
  label,
  value,
  icon = '📊',                      // Valor por defecto si no se pasa ícono
  color = 'from-blue-600 to-indigo-600'  // Gradiente por defecto
}: Props) => {
  const [isPulsing, setIsPulsing] = useState(false)
  const prevValue = useRef(value)

  // Detecta si el valor cambió y activa animación temporal
  useEffect(() => {
    if (value > prevValue.current) {
      setIsPulsing(true)
      const timeout = setTimeout(() => setIsPulsing(false), 1000)
      prevValue.current = value
      return () => clearTimeout(timeout)
    }
  }, [value])

  return (
    <div
      className={`
        w-full sm:w-auto flex-1 rounded-2xl px-6 py-4 shadow-xl bg-gradient-to-br ${color} text-white
        transition-all duration-300 ease-in-out
        ${isPulsing ? 'ring-4 ring-yellow-400/60 scale-[1.04] animate-glow' : 'hover:scale-[1.02]'}
      `}
    >
      {/* Contenedor del ícono y la etiqueta */}
      <div className="flex items-center justify-between mb-3">
        {/* Icono grande decorativo */}
        <div className={`text-4xl ${isPulsing ? 'animate-bounce-slow' : ''}`}>
          {icon}
        </div>

        {/* Título en la esquina superior derecha */}
        <div className="text-xs font-bold uppercase tracking-wide text-white/90 text-right">
          {label}
        </div>
      </div>

      {/* Valor numérico destacado, alineado a la derecha */}
      <p className="text-4xl font-extrabold text-right leading-none transition-all duration-500 ease-in-out">
        {value}
      </p>
    </div>
  )
}

export default StatsCard
