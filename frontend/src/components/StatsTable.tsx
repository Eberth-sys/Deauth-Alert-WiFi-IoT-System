//frontend\src\components\StatsTable.tsx

type Props = {
  title: string
  headers: string[]
  data: { [key: string]: any }[]
}

const StatsTable = ({ title, headers, data }: Props) => {
  return (
    <div className="w-full space-y-2">
      <h3 className="text-lg sm:text-xl font-semibold text-white">{title}</h3>
      <div className="overflow-x-auto rounded-xl shadow-md ring-1 ring-gray-700 bg-gray-900/70 backdrop-blur-sm">
        <table className="min-w-full text-sm text-gray-100">
          <thead>
            <tr className="bg-gradient-to-r from-indigo-700 via-purple-700 to-pink-700 text-white uppercase text-xs tracking-wider">
              {headers.map((h) => (
                <th key={h} className="px-4 py-3 whitespace-nowrap text-left">
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.map((row, idx) => (
              <tr
                key={idx}
                className={`transition-all duration-200 hover:bg-gray-700/40 ${
                  idx % 2 === 0 ? 'bg-gray-800/40' : 'bg-gray-700/20'
                }`}
              >
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
