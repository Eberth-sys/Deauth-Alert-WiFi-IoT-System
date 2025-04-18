// frontend/src/components/AlertRow.tsx

import { getAlertIndicatorColor, getAlertIndicatorText, getHeatColor, formatDate } from './utils/formatters'

type Props = {
  canal: number
  count: number
  lastSeen: string
  spoofed_bssid: string
  target_mac: string
  index: number
}

const AlertRow = ({ canal, count, lastSeen, spoofed_bssid, target_mac, index }: Props) => {
  return (
    <tr className={index % 2 === 0 ? 'bg-gray-700' : 'bg-gray-800'}>
      <td className="px-4 py-2 text-center">{canal}</td>

      {/* Aplicamos heat color según el número de alertas */}
      <td className={`px-4 py-2 text-center font-bold ${getHeatColor(count)}`}>
        {count}
      </td>

      <td className="px-4 py-2 text-center">{formatDate(lastSeen)}</td>
      <td className="px-4 py-2 text-center">{spoofed_bssid}</td>
      <td className="px-4 py-2 text-center">{target_mac}</td>

      {/* Indicador */}
      <td className="px-4 py-2 text-center">
        <span className={`text-xs px-2 py-1 rounded-full ${getAlertIndicatorColor(count)}`}>
          {getAlertIndicatorText(count)}
        </span>
      </td>
    </tr>
  )
}

export default AlertRow
