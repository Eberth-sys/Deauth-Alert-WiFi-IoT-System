// src/components/AlertRow.tsx

type Props = {
    nodo_iot: string
    canal: number
    count: number
    lastSeen: string
    spoofed_bssid: string
    target_mac: string
    isConnected: boolean
    lastConnection: string
    index: number
  }
  
  const AlertRow = ({
    nodo_iot,
    canal,
    count,
    lastSeen,
    spoofed_bssid,
    target_mac,
    isConnected,
    index
  }: Props) => {
    const getHeatColor = (count: number) => {
      if (count >= 100) return 'bg-red-600 text-white'
      if (count >= 50) return 'bg-orange-500 text-white'
      if (count >= 10) return 'bg-yellow-400 text-black'
      return 'bg-green-400 text-black'
    }
  
    const getConnectionStatusStyle = (connected: boolean) =>
      connected ? 'text-green-400' : 'text-red-400'
    const getConnectionStatusText = (connected: boolean) =>
      connected ? 'Conectado' : 'Desconectado'
    const getAlertIndicatorColor = (count: number) =>
      count > 0 ? 'bg-red-500' : 'bg-green-500'
    const getAlertIndicatorText = (count: number) =>
      count > 0 ? 'Alerta' : 'Ok'
  
    return (
      <tr
        className={`${
          index % 2 === 0 ? 'bg-gray-700' : 'bg-gray-800'
        } hover:bg-gray-600 transition-all`}
      >
        <td className="px-2 py-1 border-b border-gray-700">{nodo_iot}</td>
        <td className="px-2 py-1 border-b border-gray-700">{canal}</td>
        <td className={`px-2 py-1 border-b border-gray-700 font-bold text-center ${getHeatColor(count)}`}>
          {count}
        </td>
        <td className="px-2 py-1 border-b border-gray-700">
          {lastSeen !== '-' ? new Date(lastSeen).toLocaleString() : '-'}
        </td>
        <td className="px-2 py-1 border-b border-gray-700">{spoofed_bssid}</td>
        <td className="px-2 py-1 border-b border-gray-700">{target_mac}</td>
        <td className="px-2 py-1 border-b border-gray-700">
          <span className={getConnectionStatusStyle(isConnected)}>
            {getConnectionStatusText(isConnected)}
          </span>
        </td>
        <td className="px-2 py-1 border-b border-gray-700">
          <div className="flex items-center">
            <div className={`w-3 h-3 rounded-full mr-2 ${getAlertIndicatorColor(count)}`} />
            <span>{getAlertIndicatorText(count)}</span>
          </div>
        </td>
      </tr>
    )
  }
  
  export default AlertRow
  