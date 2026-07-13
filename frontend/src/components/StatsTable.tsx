//frontend\src\components\StatsTable.tsx

// Props que recibe el componente:
// - title: título que se muestra encima de la tabla
// - headers: lista de nombres de columnas a mostrar
// - data: lista de objetos con la información a renderizar en cada fila
type Props = {
  title: string
  headers: string[]
  data: { [key: string]: string | number }[]  // Diccionario de clave/valor por fila
}

// Componente para mostrar estadísticas tabulares con estilo visual atractivo
const StatsTable = ({ title, headers, data }: Props) => {
  return (
    <div className="w-full space-y-2">
      
      {/* Título descriptivo de la tabla */}
      <h3 className="text-lg sm:text-xl font-semibold text-white">{title}</h3>

      {/* Contenedor visual con estilos de scroll horizontal y efecto vidrio */}
      <div className="overflow-x-auto rounded-xl shadow-md ring-1 ring-gray-700 bg-gray-900/70 backdrop-blur-sm">
        
        {/* Tabla de estilo claro sobre fondo oscuro */}
        <table className="min-w-full text-sm text-gray-100">
          
          {/* Encabezado con gradiente de colores y estilo mayúsculas */}
          <thead>
            <tr className="bg-gradient-to-r from-indigo-700 via-purple-700 to-pink-700 text-white uppercase text-xs tracking-wider">
              {headers.map((h) => (
                <th key={h} className="px-4 py-3 whitespace-nowrap text-left">
                  {h}
                </th>
              ))}
            </tr>
          </thead>

          {/* Cuerpo de la tabla: una fila por cada elemento en `data` */}
          <tbody>
            {data.map((row, idx) => (
              <tr
                key={idx}
                className={`transition-all duration-200 hover:bg-gray-700/40 ${
                  idx % 2 === 0 ? 'bg-gray-800/40' : 'bg-gray-700/20'
                }`}
              >
                {/* Celdas generadas según los headers, accediendo con claves en minúsculas */}
                {headers.map((h) => (
                  <td key={h} className="px-4 py-3 whitespace-nowrap">
                    {row[h.toLowerCase()]}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>

        </table>
      </div>
    </div>
  )
}

export default StatsTable
