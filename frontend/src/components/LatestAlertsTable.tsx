//frontend\src\components\LatestAlertsTable.tsx

import type { AlertEvent } from './types'
import { getEventTypeBadge } from './utils/formatters'

// Props que recibe el componente: una lista de alertas por-evento
type Props = {
  alerts: AlertEvent[]
}

// Componente funcional que renderiza una tabla con las últimas alertas registradas
const LatestAlertsTable = ({ alerts }: Props) => {
  return (
    <div className="w-full space-y-2">
      
      {/* Título de la sección */}
      <h3 className="text-xl font-bold text-purple-300">
        🔟 Últimas alertas registradas
      </h3>

      {/* Contenedor con scroll horizontal, estilo visual y efecto de desenfoque */}
      <div className="overflow-x-auto rounded-xl shadow-lg ring-1 ring-purple-700/30 bg-gray-900/80 backdrop-blur">
        
        {/* Tabla principal con estilos en Tailwind */}
        <table className="min-w-full text-sm text-gray-100">
          
          {/* Cabecera de la tabla con estilos de fondo y letras en mayúsculas */}
          <thead>
            <tr className="bg-gradient-to-r from-purple-700 via-pink-700 to-red-600 text-white text-xs uppercase tracking-wider">
              <th className="px-4 py-3 whitespace-nowrap">ID</th>
              <th className="px-4 py-3 whitespace-nowrap">Nodo IoT</th>
              <th className="px-4 py-3 whitespace-nowrap">Tipo</th>
              <th className="px-4 py-3 whitespace-nowrap">Canal</th>
              <th className="px-4 py-3 whitespace-nowrap">Target MAC</th>
              <th className="px-4 py-3 whitespace-nowrap">BSSID suplantado</th>
              <th className="px-4 py-3 whitespace-nowrap">Fecha y hora</th>
            </tr>
          </thead>

          {/* Cuerpo de la tabla, recorriendo cada alerta recibida por props */}
          <tbody>
            {alerts.map((a) => {
              const badge = getEventTypeBadge(a.event_type)
              return (
              <tr
                key={a.id} // Clave única por cada alerta
                className="transition hover:bg-gray-700/50 even:bg-gray-800/40 odd:bg-gray-700/20"
              >
                <td className="px-4 py-3">{a.id}</td>
                <td className="px-4 py-3">{a.nodo_iot}</td>
                <td className="px-4 py-3"><span className={badge.className}>{badge.label}</span></td>
                <td className="px-4 py-3">{a.canal}</td>
                <td className="px-4 py-3">{a.target_mac}</td>
                <td className="px-4 py-3">{a.spoofed_bssid}</td>

                {/* Convertimos la fecha del timestamp en formato legible */}
                <td className="px-4 py-3 text-gray-300">
                  {new Date(a.timestamp).toLocaleString()}
                </td>
              </tr>
              )
            })}
          </tbody>

        </table>
      </div>
    </div>
  )
}

export default LatestAlertsTable
