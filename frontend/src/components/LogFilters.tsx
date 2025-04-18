// frontend/src/components/LogFilters.tsx

import React from 'react'

// Tipos de niveles de log disponibles
type LogLevel = 'ALL' | 'INFO' | 'WARNING' | 'ERROR' | 'CRITICAL'

// Props que recibe el componente LogFilters
interface LogFiltersProps {
  selectedLevel: LogLevel                 // Nivel actualmente seleccionado
  onSelectLevel: (level: LogLevel) => void  // Función que se llama al seleccionar un nuevo nivel
}

// Lista de niveles que se muestran como botones
const levels: LogLevel[] = ['ALL', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']

// Colores asociados a cada nivel de log para los botones
const levelColors: Record<LogLevel, string> = {
  ALL: 'bg-gray-500',
  INFO: 'bg-green-500',
  WARNING: 'bg-yellow-500',
  ERROR: 'bg-red-500',
  CRITICAL: 'bg-pink-500',
}

// Componente de filtro de logs por nivel
const LogFilters: React.FC<LogFiltersProps> = ({ selectedLevel, onSelectLevel }) => {
  return (
    // Contenedor flexible que centra los botones con separación entre ellos
    <div className="flex flex-wrap gap-2 justify-center mb-6">
      {levels.map((level) => (
        <button
          key={level}
          onClick={() => onSelectLevel(level)} // Al hacer clic cambia el nivel seleccionado
          className={`text-white font-semibold py-1 px-3 rounded shadow transition-all duration-200 ${
            levelColors[level]
          } ${selectedLevel === level ? 'ring-2 ring-white' : 'opacity-80 hover:opacity-100'}`}
        >
          {level}
        </button>
      ))}
    </div>
  )
}

export default LogFilters
