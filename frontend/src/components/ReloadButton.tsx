// frontend/src/components/ReloadButton.tsx

import React from 'react'

// Props que recibe el botón: una función que se ejecuta al hacer clic
type Props = {
  onClick: () => void
}

// Componente de botón reutilizable para recargar el log
const ReloadButton = ({ onClick }: Props) => {
  return (
    <div className="flex justify-center mb-6">
      <button
        onClick={onClick}
        className="bg-yellow-500 hover:bg-yellow-600 text-white font-semibold py-2 px-5 rounded shadow transition-all duration-200"
      >
        🔄 Recargar logs
      </button>
    </div>
  )
}

export default ReloadButton

  
