//frontend\src\components\DownloadButton.tsx

import React from 'react'

// Props que recibe el botón: una función que se ejecuta al hacer clic
type Props = {
  onClick: () => void
}

// Componente de botón reutilizable para descargar el archivo
const DownloadButton = ({ onClick }: Props) => {
  return (
    // Contenedor centrado para el botón
    <div className="flex justify-center mb-6">
      <button
        onClick={onClick}
        className="bg-transparent border-2 border-blue-400 text-blue-300 hover:bg-blue-500 hover:text-white font-semibold py-2 px-5 rounded transition duration-300 shadow-md">
        📥 Descargar archivo
      </button>
    </div>
  )
}

export default DownloadButton
