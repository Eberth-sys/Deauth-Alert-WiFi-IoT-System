// src/components/TableHeader.tsx

const TableHeader = () => (
    <thead className="bg-gradient-to-r from-blue-600 to-blue-400 text-white uppercase tracking-wider">
      <tr>
        <th className="px-2 py-1 text-left">Nodo IoT</th>
        <th className="px-2 py-1 text-left">Canal</th>
        <th className="px-2 py-1 text-center">Nº alertas</th>
        <th className="px-2 py-1 text-left">Última alerta</th>
        <th className="px-2 py-1 text-left">BSSID suplantado</th>
        <th className="px-2 py-1 text-left">MAC objetivo</th>
        <th className="px-2 py-1 text-left">Estado del nodo</th>
        <th className="px-2 py-1 text-left">Indicador</th>
      </tr>
    </thead>
  )
  
  export default TableHeader
  