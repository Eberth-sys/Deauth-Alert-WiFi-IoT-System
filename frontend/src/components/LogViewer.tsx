// frontend/src/components/LogViewer.tsx

import React from 'react'

// Props que acepta el componente LogViewer
interface LogViewerProps {
  lines: string[]                   // Las líneas del archivo de logs
  error: string | null             // Posible mensaje de error
  selectedLevel: 'ALL' | 'INFO' | 'WARNING' | 'ERROR' | 'CRITICAL'  // Nivel de filtro seleccionado
}

// Función para determinar el color del texto según el tipo de mensaje del log
const getLineColor = (line: string) => {
  if (line.includes('ERROR')) return 'text-red-400'
  if (line.includes('WARNING')) return 'text-yellow-400'
  if (line.includes('CRITICAL')) return 'text-pink-400 font-bold'
  if (line.includes('INFO')) return 'text-green-400'
  return 'text-white' // Default para líneas sin nivel reconocido
}

// Componente que muestra las líneas de log aplicando el filtro de nivel
const LogViewer: React.FC<LogViewerProps> = ({ lines, error, selectedLevel }) => {
  // Filtra las líneas en función del nivel seleccionado, o muestra todas si es "ALL"
  const filteredLines =
    selectedLevel === 'ALL'
      ? lines
      : lines.filter((line) => line.includes(selectedLevel))

  return (
    // Contenedor visual con scroll, estilo de terminal y diseño responsivo
    <div className="bg-gray-800 border border-blue-600 p-6 rounded-lg shadow-xl max-h-[70vh] overflow-y-auto font-mono text-sm whitespace-pre-wrap w-full max-w-3xl tracking-tight">
      {/* Si hay un error, lo muestra; si no, renderiza las líneas filtradas */}
      {error ? (
        <p className="text-red-500 text-center font-semibold">{error}</p>
      ) : (
        filteredLines.map((line, i) => (
          <p key={i} className={getLineColor(line)}>
            {line}
          </p>
        ))
      )}
    </div>
  )
}

export default LogViewer
