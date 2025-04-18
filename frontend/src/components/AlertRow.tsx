// frontend/src/components/AlertRow.tsx

// Importamos funciones auxiliares para formato de fecha, colores y etiquetas
import {
  getAlertIndicatorColor,
  getAlertIndicatorText,
  getHeatColor,
  formatDate
} from './utils/formatters'

// Tipado de las props que recibe el componente
type Props = {
  canal: number
  count: number
  lastSeen: string
  spoofed_bssid: string
  target_mac: string
  index: number // Para aplicar zebra-striping (colores alternos por fila)
}

// Componente funcional que representa una fila de la tabla de alertas
const AlertRow = ({ canal, count, lastSeen, spoofed_bssid, target_mac, index }: Props) => {
  return (
    // Alternancia de color de fondo por fila (gris oscuro y más oscuro)
    <tr className={index % 2 === 0 ? 'bg-gray-700' : 'bg-gray-800'}>
      
      {/* Canal en el que se detectó la alerta */}
      <td className="px-4 py-2 text-center">{canal}</td>

      {/* Conteo de alertas con color tipo heatmap según severidad */}
      <td className={`px-4 py-2 text-center font-bold ${getHeatColor(count)}`}>
        {count}
      </td>

      {/* Fecha formateada de la última alerta */}
      <td className="px-4 py-2 text-center">{formatDate(lastSeen)}</td>

      {/* Dirección BSSID suplantada */}
      <td className="px-4 py-2 text-center">{spoofed_bssid}</td>

      {/* Dirección MAC objetivo del ataque */}
      <td className="px-4 py-2 text-center">{target_mac}</td>

      {/* Indicador visual del estado: "Alerta" o "Ok", con colores personalizados */}
      <td className="px-4 py-2 text-center">
        <span className={`text-xs px-2 py-1 rounded-full ${getAlertIndicatorColor(count)}`}>
          {getAlertIndicatorText(count)}
        </span>
      </td>
    </tr>
  )
}

export default AlertRow
