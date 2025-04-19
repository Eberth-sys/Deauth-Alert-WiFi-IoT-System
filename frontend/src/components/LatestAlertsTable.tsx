//frontend\src\components\LatestAlertsTable.tsx

// Definimos el tipo de dato que representa una alerta individual
type Alert = {
  id: number                     // ID único de la alerta
  nodo_iot: string               // Nombre del nodo IoT que detectó la alerta
  canal: number                 // Canal WiFi donde se detectó la actividad
  target_mac: string           // MAC del dispositivo objetivo del ataque
  spoofed_bssid: string        // BSSID que fue suplantado (spoofed)
  timestamp: string            // Fecha y hora del evento
}

// Props que recibe el componente: una lista de alertas
type Props = {
  alerts: Alert[]              // Arreglo de objetos tipo Alert
}

// Componente funcional que renderiza una tabla con las últimas alertas registradas
const LatestAlertsTable = ({ alerts }: Props) => {
  return (
    <div className="w-full space-y-2">
      
      {/* Título de la sección */}
      <h3 className="text-xl font-bold text-purple-300">
        🔟 Últimas Alertas Registradas
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
              <th className="px-4 py-3 whitespace-nowrap">Canal</th>
              <th className="px-4 py-3 whitespace-nowrap">Target MAC</th>
              <th className="px-4 py-3 whitespace-nowrap">BSSID Suplantado</th>
              <th className="px-4 py-3 whitespace-nowrap">Fecha y Hora</th>
            </tr>
          </thead>

          {/* Cuerpo de la tabla, recorriendo cada alerta recibida por props */}
          <tbody>
            {alerts.map((a) => (
              <tr
                key={a.id} // Clave única por cada alerta
                className="transition hover:bg-gray-700/50 even:bg-gray-800/40 odd:bg-gray-700/20"
              >
                <td className="px-4 py-3">{a.id}</td>
                <td className="px-4 py-3">{a.nodo_iot}</td>
                <td className="px-4 py-3">{a.canal}</td>
                <td className="px-4 py-3">{a.target_mac}</td>
                <td className="px-4 py-3">{a.spoofed_bssid}</td>

                {/* Convertimos la fecha del timestamp en formato legible */}
                <td className="px-4 py-3 text-gray-300">
                  {new Date(a.timestamp).toLocaleString()}
                </td>
              </tr>
            ))}
          </tbody>

        </table>
      </div>
    </div>
  )
}

export default LatestAlertsTable
