// frontend/src/components/BackToHomeButton.tsx

import React from 'react'

const BackToHomeButton = () => {
  return (
    <div className="w-full flex justify-end mb-4">
      <a
        href="/"
        className="bg-gradient-to-r from-gray-700 to-gray-900 hover:from-blue-600 hover:to-blue-800 text-white font-semibold py-2 px-5 rounded shadow transition-all duration-300 flex items-center gap-2"
      >
        <span className="text-xl">🏠</span>
        <span className="text-sm sm:inline">Volver al inicio</span>
      </a>
    </div>
  )
}

export default BackToHomeButton


