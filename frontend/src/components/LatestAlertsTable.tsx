//frontend\src\components\LatestAlertsTable.tsx

type Alert = {
  id: number
  nodo_iot: string
  canal: number
  target_mac: string
  spoofed_bssid: string
  timestamp: string
}

type Props = {
  alerts: Alert[]
}

const LatestAlertsTable = ({ alerts }: Props) => {
  return (
    <div className="w-full space-y-2">
      <h3 className="text-xl font-bold text-purple-300">
        🔟 Últimas Alertas Registradas
      </h3>
      <div className="overflow-x-auto rounded-xl shadow-lg ring-1 ring-purple-700/30 bg-gray-900/80 backdrop-blur">
        <table className="min-w-full text-sm text-gray-100">
          <thead>
            <tr className="bg-gradient-to-r from-purple-700 via-pink-700 to-red-600 text-white text-xs uppercase tracking-wider">
              <th className="px-4 py-3 whitespace-nowrap">ID</th>
              <th className="px-4 py-3 whitespace-nowrap">Nodo IoT</th>
              <th className="px-4 py-3 whitespace-nowrap">Canal</th>
              <th className="px-4 py-3 whitespace-nowrap">Target MAC</th>
              <th className="px-4 py-3 whitespace-nowrap">BSSID Suplantado</th>
              <th className="px-4 py-3 whitespace-nowrap">Fecha y Hora</th>
            </tr>
          </thead>
          <tbody>
            {alerts.map((a) => (
              <tr
                key={a.id}
                className="transition hover:bg-gray-700/50 even:bg-gray-800/40 odd:bg-gray-700/20"
              >
                <td className="px-4 py-3">{a.id}</td>
                <td className="px-4 py-3">{a.nodo_iot}</td>
                <td className="px-4 py-3">{a.canal}</td>
                <td className="px-4 py-3">{a.target_mac}</td>
                <td className="px-4 py-3">{a.spoofed_bssid}</td>
                <td className="px-4 py-3 text-gray-300">{new Date(a.timestamp).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default LatestAlertsTable
