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
  ALL: 'from-gray-600 to-gray-700',
  INFO: 'from-green-500 to-emerald-600',
  WARNING: 'from-yellow-400 to-yellow-600',
  ERROR: 'from-red-500 to-red-700',
  CRITICAL: 'from-pink-500 to-fuchsia-600',
}

// Íconos por nivel para mayor visualización
const levelIcons: Record<LogLevel, string> = {
  ALL: '📋',
  INFO: 'ℹ️',
  WARNING: '⚠️',
  ERROR: '❌',
  CRITICAL: '🚨',
}

// Componente de filtro de logs por nivel
const LogFilters: React.FC<LogFiltersProps> = ({ selectedLevel, onSelectLevel }) => {
  return (
    // Contenedor flexible que centra los botones con separación entre ellos
    <div className="flex flex-wrap gap-3 justify-center mb-6">
      {levels.map((level) => (
        <button
          key={level}
          onClick={() => onSelectLevel(level)} // Al hacer clic cambia el nivel seleccionado
          className={`
            flex items-center gap-2 px-4 py-1.5 rounded-full shadow-md text-sm font-semibold text-white 
            bg-gradient-to-br ${levelColors[level]} 
            transition-all duration-200 
            ${selectedLevel === level ? 'ring-2 ring-offset-2 ring-white scale-105' : 'opacity-80 hover:opacity-100'}
          `}
        >
          <span>{levelIcons[level]}</span>
          {level}
        </button>
      ))}
    </div>
  )
}

export default LogFilters
