// frontend\src\components\ReportsTable.tsx

type AlertData = {
    id: number
    nodo_iot: string
    spoofed_bssid: string
    target_mac: string
    bssid: string
    canal: number
    timestamp: string
  }
  
  type Props = {
    alerts: AlertData[]
  }
  
  const ReportsTable = ({ alerts }: Props) => {
    return (
      <div className="overflow-x-auto mt-4">
        <table className="min-w-full table-auto text-sm text-left border border-gray-700">
          <thead className="bg-gradient-to-r from-purple-600 to-pink-600 text-white">
            <tr>
              <th className="px-4 py-2">ID</th>
              <th className="px-4 py-2">Nodo</th>
              <th className="px-4 py-2">Canal</th>
              <th className="px-4 py-2">MAC Objetivo</th>
              <th className="px-4 py-2">BSSID Suplantado</th>
              <th className="px-4 py-2">Fecha</th>
            </tr>
          </thead>
          <tbody>
            {alerts.map((alert) => (
              <tr key={alert.id} className="odd:bg-gray-800 even:bg-gray-700">
                <td className="px-4 py-2">{alert.id}</td>
                <td className="px-4 py-2">{alert.nodo_iot}</td>
                <td className="px-4 py-2">{alert.canal}</td>
                <td className="px-4 py-2">{alert.target_mac}</td>
                <td className="px-4 py-2">{alert.spoofed_bssid}</td>
                <td className="px-4 py-2">{new Date(alert.timestamp).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    )
  }
  
  export default ReportsTable
  