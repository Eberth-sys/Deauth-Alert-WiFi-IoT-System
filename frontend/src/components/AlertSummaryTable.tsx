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
      <div className="w-full max-w-7xl">
        {/* Desktop TABLE */}
        <div className="hidden md:block overflow-x-auto rounded-2xl shadow-2xl ring-1 ring-gray-700 bg-gray-900">
          <table className="min-w-full table-auto text-sm text-gray-100">
            <thead className="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 text-white">
              <tr>
                <th className="px-4 py-3 text-left">Canal</th>
                <th className="px-4 py-3 text-center">Nº Alertas</th>
                <th className="px-4 py-3 text-left">Última Alerta</th>
                <th className="px-4 py-3 text-left">BSSID Suplantado</th>
                <th className="px-4 py-3 text-left">MAC Objetivo</th>
                <th className="px-4 py-3 text-center">Indicador</th>
              </tr>
            </thead>
            <tbody>
              {data.map((row, idx) => (
                <tr
                  key={idx}
                  className={`transition-all hover:bg-gray-700/60 ${
                    idx % 2 === 0 ? 'bg-gray-800/40' : 'bg-gray-800/20'
                  } ${row.count >= 100 ? 'border-l-4 border-pink-500' : ''}`}
                >
                  <td className="px-4 py-3">{row.canal}</td>
                  <td className={`px-4 py-3 text-center font-semibold ${getHeatColor(row.count)}`}>
                    {row.count}
                  </td>
                  <td className="px-4 py-3">{formatDate(row.lastSeen)}</td>
                  <td className="px-4 py-3">{row.spoofed_bssid}</td>
                  <td className="px-4 py-3">{row.target_mac}</td>
                  <td className="px-4 py-3 text-center">
                    <span
                      className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium shadow-md transition-all ${getAlertIndicatorColor(
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

        {/* Mobile CARDS */}
        <div className="block md:hidden space-y-4 mt-4">
          {data.map((row, idx) => (
            <div
              key={idx}
              className={`rounded-xl p-4 shadow-lg flex flex-col space-y-2 border border-gray-700 ${
                row.count >= 100 ? 'border-pink-500/60' : 'bg-gray-800/40'
              }`}
            >
              <div className="text-sm text-gray-300">
                <strong>Canal:</strong> {row.canal}
              </div>
              <div className="text-sm text-gray-300">
                <strong>Última Alerta:</strong> {formatDate(row.lastSeen)}
              </div>
              <div className="text-sm text-gray-300">
                <strong>BSSID:</strong> {row.spoofed_bssid}
              </div>
              <div className="text-sm text-gray-300">
                <strong>MAC Objetivo:</strong> {row.target_mac}
              </div>
              <div className="text-sm text-gray-300">
                <strong>Alertas:</strong>{' '}
                <span className={`font-bold ${getHeatColor(row.count)}`}>{row.count}</span>
              </div>
              <div>
                <span
                  className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium ${getAlertIndicatorColor(
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
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default AlertSummaryTable
