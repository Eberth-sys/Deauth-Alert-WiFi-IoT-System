// frontend/src/components/NodeStatusTable.tsx

import { NodeStatus } from './types'
import { getConnectionStatusStyle, getConnectionStatusText } from './utils/formatters'

type Props = {
  status: NodeStatus[]
}

const NodeStatusTable = ({ status }: Props) => {
  return (
    <div className="mb-10">
      <h3 className="text-xl text-green-400 font-bold mb-2">🔌 Estado Actual de los Nodos ESP32</h3>
      <div className="overflow-x-auto rounded-lg shadow-lg">
        <table className="w-full bg-gray-800 text-sm text-gray-100">
          <thead className="bg-green-700 text-white">
            <tr>
              <th className="px-3 py-2 text-left">Nodo IoT</th>
              <th className="px-3 py-2 text-left">Estado del Nodo</th>
            </tr>
          </thead>
          <tbody>
            {status.map((node, idx) => (
              <tr key={idx} className={idx % 2 === 0 ? 'bg-gray-700' : 'bg-gray-800'}>
                <td className="px-3 py-2">{node.device_name}</td>
                <td className="px-3 py-2">
                  <span className={getConnectionStatusStyle(node.status === 'connected')}>
                    {getConnectionStatusText(node.status === 'connected')}
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

export default NodeStatusTable
