import { AggregatedAlert } from './types'
import { formatDate, getAlertIndicatorColor, getAlertIndicatorText } from './utils/formatters'

type Props = {
  data: AggregatedAlert[]
}

const AlertSummaryTable = ({ data }: Props) => {
  return (
    <div className="mb-10 flex justify-center">
      <div className="overflow-x-auto rounded-lg shadow-lg">
        <table className="table-auto bg-gray-800 text-sm text-gray-100">
          <thead className="bg-blue-700 text-white">
            <tr>
              <th className="px-2 py-1 text-left">Canal</th>
              <th className="px-2 py-1 text-center">Nº Alertas</th>
              <th className="px-2 py-1">Última Alerta</th>
              <th className="px-2 py-1">BSSID Suplantado</th>
              <th className="px-2 py-1">MAC Objetivo</th>
              <th className="px-2 py-1 text-center">Indicador</th>
            </tr>
          </thead>
          <tbody>
            {data.map((row, idx) => (
              <tr key={idx} className={idx % 2 === 0 ? 'bg-gray-700' : 'bg-gray-800'}>
                <td className="px-2 py-1">{row.canal}</td>
                <td className="px-2 py-1 text-center font-bold">{row.count}</td>
                <td className="px-2 py-1">{formatDate(row.lastSeen)}</td>
                <td className="px-2 py-1">{row.spoofed_bssid}</td>
                <td className="px-2 py-1">{row.target_mac}</td>
                <td className="px-2 py-1 text-center">
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
