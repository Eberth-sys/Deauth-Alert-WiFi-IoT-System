// frontend\src\pages\LogsPage.tsx
import { useEffect, useState } from 'react'

const LOG_FILE = 'ble_events.log'
const API_BASE = 'http://192.168.255.132:8000/logs'

const LogsPage = () => {
  const [logContent, setLogContent] = useState<string>('')

  useEffect(() => {
    const fetchLogs = async () => {
      try {
        const response = await fetch(`${API_BASE}/${LOG_FILE}`)
        const text = await response.text()
        setLogContent(text)
      } catch (error) {
        setLogContent('❌ Error al cargar el archivo de logs')
      }
    }

    fetchLogs()
  }, [])

  const handleDownload = () => {
    const link = document.createElement('a')
    link.href = `${API_BASE}/${LOG_FILE}`
    link.download = LOG_FILE
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  return (
    <div className="bg-gray-900 min-h-screen text-white p-6">
      <h2 className="text-2xl font-bold mb-4 text-blue-400 text-center">
        Visualizador de Logs BLE
      </h2>

      <div className="mb-4 text-center">
        <button
          onClick={handleDownload}
          className="bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 px-4 rounded shadow"
        >
          Descargar archivo
        </button>
      </div>

      <div className="bg-gray-800 p-4 rounded overflow-auto max-h-[70vh] font-mono text-sm whitespace-pre-wrap">
        {logContent}
      </div>
    </div>
  )
}

export default LogsPage
