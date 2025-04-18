import { AggregatedAlert } from './types'
import {
  formatDate,
  getAlertIndicatorColor,
  getAlertIndicatorText,
  getHeatColor
} from './utils/formatters'

type Props = {
  data: AggregatedAlert[]
}

const AlertSummaryTable = ({ data }: Props) => {
  return (
    <div className="mb-10 flex justify-center font-inter">
      <div className="overflow-x-auto rounded-2xl shadow-2xl ring-1 ring-gray-700 bg-gray-900">
        <table className="min-w-full table-auto text-sm text-gray-100">
          <thead>
            <tr className="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 text-white">
              <th className="px-6 py-3 text-left uppercase tracking-wider">Canal</th>
              <th className="px-6 py-3 text-center uppercase tracking-wider">Nº Alertas</th>
              <th className="px-6 py-3 text-left uppercase tracking-wider">Última Alerta</th>
              <th className="px-6 py-3 text-left uppercase tracking-wider">BSSID Suplantado</th>
              <th className="px-6 py-3 text-left uppercase tracking-wider">MAC Objetivo</th>
              <th className="px-6 py-3 text-center uppercase tracking-wider">Indicador</th>
            </tr>
          </thead>
          <tbody>
            {data.map((row, idx) => (
              <tr
                key={idx}
                className={`transition-all duration-300 ease-in-out hover:bg-gray-700/60 ${
                  idx % 2 === 0 ? 'bg-gray-800/50' : 'bg-gray-800/30'
                } ${row.count >= 100 ? 'border-l-4 border-pink-500' : ''}`}
              >
                <td className="px-6 py-3 border-t border-gray-700">{row.canal}</td>
                <td
                  className={`px-6 py-3 border-t border-gray-700 text-center font-semibold ${getHeatColor(
                    row.count
                  )}`}
                >
                  {row.count}
                </td>
                <td className="px-6 py-3 border-t border-gray-700">{formatDate(row.lastSeen)}</td>
                <td className="px-6 py-3 border-t border-gray-700">{row.spoofed_bssid}</td>
                <td className="px-6 py-3 border-t border-gray-700">{row.target_mac}</td>
                <td className="px-6 py-3 border-t border-gray-700 text-center">
                  <span
                    className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium shadow-md transition-all duration-300 ease-in-out ${getAlertIndicatorColor(
                      row.count
                    )}`}
                    style={{
                      background:
                        row.count > 0
                          ? 'linear-gradient(to right, #ef4444, #f97316)'
                          : 'linear-gradient(to right, #10b981, #3b82f6)',
                      color: '#fff',
                    }}
                  >
                    {row.count > 0 ? '🔴' : '🟢'} {getAlertIndicatorText(row.count)}
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
