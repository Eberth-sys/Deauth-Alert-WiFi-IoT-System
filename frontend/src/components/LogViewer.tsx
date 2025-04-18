//frontend\src\components\LogViewer.tsx

import React from 'react'
import { getLineColor } from './utils/logs' // Importa función para colorear líneas

// Props que recibe el componente: líneas del log y un error (opcional)
type Props = {
  lines: string[]
  error?: string | null
}

// Componente que muestra el contenido del log formateado y con scroll
const LogViewer = ({ lines, error }: Props) => {
  return (
    <div className="bg-gray-800 border border-blue-600 p-6 rounded-lg shadow-xl max-h-[70vh] overflow-y-auto font-mono text-sm whitespace-pre-wrap w-full max-w-3xl tracking-tight">
      {/* Si hay error lo muestra, sino recorre todas las líneas del log */}
      {error ? (
        <p className="text-red-400 text-center font-semibold">{error}</p>
      ) : (
        lines.map((line, i) => (
          <p key={i} className={getLineColor(line)}>
            {line}
          </p>
        ))
      )}
    </div>
  )
}

export default LogViewer

