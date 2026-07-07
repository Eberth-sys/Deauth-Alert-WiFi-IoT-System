//frontend\src\components\NodeStatusTable.tsx

// Importamos el tipo de datos que describe el estado de los nodos
import { NodeStatus } from './types'

// Definimos las props que el componente espera recibir
type Props = {
  status: NodeStatus[]
}

// Componente funcional principal
const NodeStatusTable = ({ status }: Props) => {
  return (
    <div className="mb-6 flex justify-center font-inter">
      {/* Contenedor de ancho máximo para limitar el tamaño de la tabla */}
      <div className="w-full max-w-xl">

        {/* TABLA para pantallas medianas en adelante */}
        <div className="hidden md:block overflow-x-auto rounded-xl shadow-md ring-1 ring-gray-700 bg-gray-900/90 backdrop-blur">
          <table className="table-auto w-full text-xs text-gray-100">
            <thead className="bg-gradient-to-r from-green-600 to-emerald-500 text-white">
              <tr>
                <th className="px-3 py-2 text-left">Nodo IoT</th>
                <th className="px-3 py-2 text-left">Estado</th>
              </tr>
            </thead>
            <tbody>
              {status.map((node, idx) => (
                <tr
                  key={idx}
                  className={`transition-all duration-200 hover:bg-gray-700/50 ${
                    idx % 2 === 0 ? 'bg-gray-800/40' : 'bg-gray-800/20'
                  }`}
                >
                  {/* Nombre del nodo */}
                  <td className="px-3 py-2">{node.device_name}</td>

                  {/* Estado de conexión con colores dinámicos y animación */}
                  <td className="px-3 py-2">
                    <span
                      className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-medium ${
                        node.status === 'connected'
                          ? 'bg-green-500/20 text-green-400 animate-pulse'
                          : 'bg-red-500/20 text-red-400'
                      }`}
                    >
                      {node.status === 'connected' ? '🟢 Conectado' : '🔴 Desconectado'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* CARDS para móviles: Vista adaptada por nodo */}
        <div className="block md:hidden space-y-3 mt-4">
          {status.map((node, idx) => (
            <div
              key={idx}
              className="rounded-xl bg-gray-800/80 backdrop-blur-md p-3 shadow-md flex flex-col space-y-1 border border-gray-700"
            >
              {/* Nombre del nodo */}
              <div className="text-sm font-semibold text-gray-200">
                <span className="text-gray-400">Nodo:</span> {node.device_name}
              </div>

              {/* Estado con colores adaptados */}
              <div>
                <span
                  className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${
                    node.status === 'connected'
                      ? 'bg-green-500/20 text-green-400 animate-pulse'
                      : 'bg-red-500/20 text-red-400'
                  }`}
                >
                  {node.status === 'connected' ? '🟢 Conectado' : '🔴 Desconectado'}
                </span>
              </div>
            </div>
          ))}
        </div>

      </div>
    </div>
  )
}

export default NodeStatusTable
