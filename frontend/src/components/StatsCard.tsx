//frontend\src\components\StatsCard.tsx

// Definición del tipo de props que recibe la tarjeta estadística
type Props = {
  label: string       // Texto descriptivo
  value: number       // Valor numérico que se muestra destacado
  icon?: string       // Icono decorativo opcional)
  color?: string      // Clases Tailwind opcionales para personalizar el gradiente
}

// Componente funcional que representa una tarjeta visual de estadística
const StatsCard = ({
  label,
  value,
  icon = '📊',                      // Valor por defecto si no se pasa ícono
  color = 'from-blue-600 to-indigo-600'  // Gradiente por defecto
}: Props) => {
  return (
    <div
      className={`w-full sm:w-auto flex-1 rounded-2xl px-6 py-4 shadow-xl 
        bg-gradient-to-br ${color} text-white 
        transform transition duration-300 hover:scale-[1.02]`}
    >
      {/* Contenedor del ícono y la etiqueta */}
      <div className="flex items-center justify-between mb-3">
        {/* Icono grande decorativo */}
        <div className="text-4xl drop-shadow-[0_1px_3px_rgba(0,0,0,0.4)]">
          {icon}
        </div>

        {/* Título en la esquina superior derecha */}
        <div className="text-xs font-bold uppercase tracking-wide text-white/90 text-right">
          {label}
        </div>
      </div>

      {/* Valor numérico destacado, alineado a la derecha */}
      <p className="text-4xl font-extrabold text-right leading-none">
        {value}
      </p>
    </div>
  )
}

export default StatsCard
