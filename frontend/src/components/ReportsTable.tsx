// frontend\src\components\ReportsTable.tsx

import type { AlertEvent } from './types'
import { getEventTypeBadge } from './utils/formatters'

// Definición de las propiedades (props) que recibe el componente: un array de alertas por-evento
type Props = {
  alerts: AlertEvent[]          // Lista de alertas a mostrar
}

// Componente que renderiza una tabla con los datos de alerta recibidos por props
const ReportsTable = ({ alerts }: Props) => {
  return (
    // Contenedor con scroll horizontal para pantallas pequeñas
    <div className="overflow-x-auto mt-4">
      
      {/* Tabla principal con estilos de bordes y texto */}
      <table className="min-w-full table-auto text-sm text-left border border-gray-700">

        {/* Encabezado con gradiente de color */}
        <thead className="bg-gradient-to-r from-purple-600 to-pink-600 text-white">
          <tr>
            <th className="px-4 py-2">ID</th>
            <th className="px-4 py-2">Nodo</th>
            <th className="px-4 py-2">Tipo</th>
            <th className="px-4 py-2">Canal</th>
            <th className="px-4 py-2">MAC objetivo</th>
            <th className="px-4 py-2">BSSID suplantado</th>
            <th className="px-4 py-2">Fecha</th>
          </tr>
        </thead>

        {/* Cuerpo de la tabla: filas de alertas */}
        <tbody>
          {alerts.map((alert) => {
            const badge = getEventTypeBadge(alert.event_type)
            return (
            <tr key={alert.id} className="odd:bg-gray-800 even:bg-gray-700">
              <td className="px-4 py-2">{alert.id}</td>
              <td className="px-4 py-2">{alert.nodo_iot}</td>
              <td className="px-4 py-2"><span className={badge.className}>{badge.label}</span></td>
              <td className="px-4 py-2">{alert.canal}</td>
              <td className="px-4 py-2">{alert.target_mac}</td>
              <td className="px-4 py-2">{alert.spoofed_bssid}</td>

              {/* Formateo de la fecha en formato local legible */}
              <td className="px-4 py-2">{new Date(alert.timestamp).toLocaleString()}</td>
            </tr>
            )
          })}
        </tbody>

      </table>
    </div>
  )
}

export default ReportsTable
