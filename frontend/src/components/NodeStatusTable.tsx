import { NodeStatus } from './types'
import { getConnectionStatusStyle, getConnectionStatusText } from './utils/formatters'

type Props = {
  status: NodeStatus[]
}

const NodeStatusTable = ({ status }: Props) => {
  return (
    <div className="mb-10 flex justify-center">
      <div className="overflow-x-auto rounded-lg shadow-lg">
        <table className="table-auto bg-gray-800 text-sm text-gray-100">
          <thead className="bg-green-700 text-white">
            <tr>
              <th className="px-2 py-1 text-left">Nodo IoT</th>
              <th className="px-2 py-1 text-left">Estado del Nodo</th>
            </tr>
          </thead>
          <tbody>
            {status.map((node, idx) => (
              <tr key={idx} className={idx % 2 === 0 ? 'bg-gray-700' : 'bg-gray-800'}>
                <td className="px-2 py-1">{node.device_name}</td>
                <td className="px-2 py-1">
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
