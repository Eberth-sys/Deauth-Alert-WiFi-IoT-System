//frontend\src\components\DownloadButton.tsx

import React from 'react'

// Props que recibe el botón: una función que se ejecuta al hacer clic
type Props = {
  onClick: () => void
}

// Componente de botón reutilizable para descargar el archivo
const DownloadButton = ({ onClick }: Props) => {
  return (
    <div className="flex justify-center mb-6">
      <button
        onClick={onClick}
        className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-5 rounded shadow transition-all duration-200"
      >
        📥 Descargar archivo
      </button>
    </div>
  )
}

export default DownloadButton
