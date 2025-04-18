//frontend\src\components\utils\logs.ts

// Función para obtener contenido del archivo desde el backend
export const fetchLogFile = async (filename: string): Promise<string[]> => {
    const response = await fetch(`http://192.168.255.132:8000/logs/${filename}`)
    const data = await response.json()
    return data.content
  }
  
  // Función para descargar el archivo de forma limpia y automática
  export const downloadLogFile = (filename: string, lines: string[]) => {
    const blob = new Blob([lines.join('\n')], { type: 'text/plain' }) // Crea un blob de texto plano
    const url = URL.createObjectURL(blob) // Crea un enlace temporal
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url) // Limpieza de memoria
  }
  
  // Función para asignar color según tipo de log
  export const getLineColor = (line: string): string => {
    if (line.includes('ERROR')) return 'text-red-400'
    if (line.includes('WARNING')) return 'text-yellow-400'
    if (line.includes('CRITICAL')) return 'text-pink-400 font-bold'
    if (line.includes('INFO')) return 'text-green-400'
    return 'text-white'
  }
  