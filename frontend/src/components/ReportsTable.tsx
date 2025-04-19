// frontend\src\components\ReportsTable.tsx

// Tipo que representa una alerta individual utilizada en los reportes personalizados
type AlertData = {
  id: number                    // Identificador único de la alerta
  nodo_iot: string              // Nodo IoT que reportó la alerta
  spoofed_bssid: string         // Dirección BSSID suplantada
  target_mac: string            // Dirección MAC del objetivo
  bssid: string                 // Dirección BSSID original
  canal: number                 // Canal en el que se detectó la actividad
  timestamp: string             // Fecha y hora del evento
}

// Definición de las propiedades (props) que recibe el componente: un array de alertas
type Props = {
  alerts: AlertData[]          // Lista de alertas a mostrar
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
            <th className="px-4 py-2">Canal</th>
            <th className="px-4 py-2">MAC Objetivo</th>
            <th className="px-4 py-2">BSSID Suplantado</th>
            <th className="px-4 py-2">Fecha</th>
          </tr>
        </thead>

        {/* Cuerpo de la tabla: filas de alertas */}
        <tbody>
          {alerts.map((alert) => (
            <tr key={alert.id} className="odd:bg-gray-800 even:bg-gray-700">
              <td className="px-4 py-2">{alert.id}</td>
              <td className="px-4 py-2">{alert.nodo_iot}</td>
              <td className="px-4 py-2">{alert.canal}</td>
              <td className="px-4 py-2">{alert.target_mac}</td>
              <td className="px-4 py-2">{alert.spoofed_bssid}</td>

              {/* Formateo de la fecha en formato local legible */}
              <td className="px-4 py-2">{new Date(alert.timestamp).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>

      </table>
    </div>
  )
}

export default ReportsTable
