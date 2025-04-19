//frontend\src\components\StatsCard.tsx

type Props = {
  label: string
  value: number
  icon?: string
  color?: string
}

const StatsCard = ({
  label,
  value,
  icon = '📊',
  color = 'from-blue-600 to-indigo-600'
}: Props) => {
  return (
    <div
      className={`w-full sm:w-auto flex-1 rounded-2xl px-6 py-4 shadow-xl bg-gradient-to-br ${color} text-white transform transition duration-300 hover:scale-[1.02]`}
    >
      <div className="flex items-center justify-between mb-3">
        <div className="text-4xl drop-shadow-[0_1px_3px_rgba(0,0,0,0.4)]">{icon}</div>
        <div className="text-xs font-bold uppercase tracking-wide text-white/90 text-right">
          {label}
        </div>
      </div>
      <p className="text-4xl font-extrabold text-right leading-none">{value}</p>
    </div>
  )
}

export default StatsCard
