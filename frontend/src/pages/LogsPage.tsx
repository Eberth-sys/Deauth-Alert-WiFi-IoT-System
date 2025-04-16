// frontend/src/pages/LogsPage.tsx

import { useEffect, useState } from 'react' // Importamos hooks de React

// Nombre del archivo de logs y la URL base del backend
const LOG_FILE = 'ble_events.log'
const API_BASE = 'http://192.168.255.132:8000/logs'

// Tipo de respuesta esperada desde el backend
type LogResponse = {
  filename: string
  content: string[] // Contenido del log como arreglo de líneas
}

const LogsPage = () => {
  // Estado para almacenar líneas del archivo log
  const [logLines, setLogLines] = useState<string[]>([])
  // Estado para manejar errores si ocurren durante fetch
  const [error, setError] = useState<string | null>(null)

  // useEffect se ejecuta una vez al cargar el componente
  useEffect(() => {
    const fetchLogs = async () => {
      try {
        // Fetch al backend para obtener el contenido del log
        const response = await fetch(`${API_BASE}/${LOG_FILE}`)
        const data: LogResponse = await response.json()
        setLogLines(data.content) // Guardamos las líneas del archivo
      } catch (error) {
        setError('❌ Error al cargar el archivo de logs')
      }
    }

    fetchLogs()
  }, [])

  // Función que permite descargar el log como archivo plano
  const handleDownload = async () => {
    try {
      // Fetch para obtener contenido
      const response = await fetch(`${API_BASE}/${LOG_FILE}`)
      const data: LogResponse = await response.json()

      // Convertimos el array en texto plano
      const blob = new Blob([data.content.join('\n')], { type: 'text/plain' })

      // Creamos enlace temporal y disparamos descarga
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = LOG_FILE
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
    } catch (error) {
      console.error('Error al descargar archivo:', error)
    }
  }

  // Determina el color de la línea en función del tipo de log
  const getLineColor = (line: string) => {
    if (line.includes('ERROR')) return 'text-red-400'
    if (line.includes('WARNING')) return 'text-yellow-400'
    if (line.includes('CRITICAL')) return 'text-pink-400 font-bold'
    if (line.includes('INFO')) return 'text-green-400'
    return 'text-white'
  }

  // Estructura visual del componente
  return (
    <div className="bg-gray-900 h-screen w-screen flex flex-col">
      {/* Encabezado superior */}
      <header className="py-6">
        <h2 className="text-3xl font-extrabold text-center text-blue-400">
          Visualizador de Logs BLE
        </h2>
      </header>

      {/* Contenedor principal con scroll vertical */}
      <main className="flex-1 overflow-y-auto px-6 pb-6 flex justify-center">
        <div className="max-w-sm w-full">
          {/* Botón de descarga centrado */}
          <div className="mb-4 text-center">
            <button
              onClick={handleDownload}
              className="bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 px-6 rounded shadow"
            >
              📥 Descargar archivo
            </button>
          </div>

          {/* Caja de logs con scroll y estilos por severidad */}
          <div className="bg-gray-800 border border-blue-600 p-4 rounded-lg shadow-lg max-h-[70vh] overflow-y-auto font-mono text-sm whitespace-pre-wrap max-w-2xl mx-auto">
            {error ? (
              <p>{error}</p> // Muestra error si falla fetch
            ) : (
              logLines.map((line, i) => (
                <p key={i} className={getLineColor(line)}>
                  {line}
                </p>
              ))
            )}
          </div>
        </div>
      </main>
    </div>
  )
}

export default LogsPage
