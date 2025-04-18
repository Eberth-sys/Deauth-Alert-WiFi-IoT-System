// frontend/src/components/BackToHomeButton.tsx

import React from 'react'

const BackToHomeButton = () => {
  return (
    <div className="w-full flex justify-end mb-6">
      <a
        href="/"
        className="group bg-gradient-to-r from-slate-700 via-gray-800 to-slate-700 hover:from-blue-600 hover:via-blue-700 hover:to-indigo-700 text-white font-semibold py-2 px-6 rounded-full shadow-lg transition-all duration-300 flex items-center gap-3 ring-1 ring-slate-600 hover:ring-blue-500"
      >
        <span className="text-2xl group-hover:animate-bounce">🏠</span>
        <span className="text-sm sm:text-base">Volver al inicio</span>
      </a>
    </div>
  )
}

export default BackToHomeButton

