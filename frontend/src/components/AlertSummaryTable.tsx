// frontend/src/components/AlertSummaryTable.tsx

import { AggregatedAlert } from './types'
import { formatDate, getAlertIndicatorColor, getAlertIndicatorText } from './utils/formatters'

type Props = {
  data: AggregatedAlert[]
}

const AlertSummaryTable = ({ data }: Props) => {
  return (
    <div className="mb-10">
      <h3 className="text-xl text-blue-400 font-bold mb-2">📡 Resumen de Alertas por Canal</h3>
      <div className="overflow-x-auto rounded-lg shadow-lg">
        <table className="w-full bg-gray-800 text-sm text-gray-100">
          <thead className="bg-blue-700 text-white">
            <tr>
              <th className="px-3 py-2 text-left">Canal</th>
              <th className="px-3 py-2 text-center">Nº Alertas</th>
              <th className="px-3 py-2">Última Alerta</th>
              <th className="px-3 py-2">BSSID Suplantado</th>
              <th className="px-3 py-2">MAC Objetivo</th>
              <th className="px-3 py-2 text-center">Indicador</th>
            </tr>
          </thead>
          <tbody>
            {data.map((row, idx) => (
              <tr key={idx} className={idx % 2 === 0 ? 'bg-gray-700' : 'bg-gray-800'}>
                <td className="px-3 py-2">{row.canal}</td>
                <td className="px-3 py-2 text-center font-bold">{row.count}</td>
                <td className="px-3 py-2">{formatDate(row.lastSeen)}</td>
                <td className="px-3 py-2">{row.spoofed_bssid}</td>
                <td className="px-3 py-2">{row.target_mac}</td>
                <td className="px-3 py-2 text-center">
                  <span className={`inline-flex items-center gap-2 ${getAlertIndicatorColor(row.count)} px-2 py-1 rounded`}>
                    {getAlertIndicatorText(row.count)}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default AlertSummaryTable
