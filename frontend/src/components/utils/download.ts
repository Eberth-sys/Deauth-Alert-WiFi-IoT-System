// frontend\src\components\utils\download.ts

/**
 * Función utilitaria que convierte un arreglo de objetos en un archivo CSV
 * y lo descarga automáticamente en el navegador del usuario.
 *
 * @param data - Arreglo de objetos con la información a exportar
 * @param filename - Nombre del archivo CSV a guardar
 */

export const downloadCSV = (data: any[], filename: string) => {
    // Si no hay datos, se detiene la función
    if (!data.length) return
  
    // Extrae los encabezados desde las claves del primer objeto
    const headers = Object.keys(data[0])
  
    // Construye el contenido del archivo CSV
    const csvRows = [
      headers.join(','), // primera fila: encabezado con nombres de columnas
      ...data.map((row) =>
        // cada fila: se convierte en una cadena CSV respetando el orden de los headers
        headers.map((field) => JSON.stringify(row[field], (_, v) => v ?? '')).join(',')
      )
    ]
  
    // Crea un archivo tipo Blob con el contenido generado
    const blob = new Blob([csvRows.join('\n')], { type: 'text/csv' })
  
    // Genera una URL temporal del archivo para descargar
    const url = URL.createObjectURL(blob)
  
    // Crea un enlace <a> oculto para activar la descarga
    const a = document.createElement('a')
    a.href = url
    a.download = `${filename}.csv`
    a.click() // Simula el clic para descargar el archivo
  
    // Libera el recurso de memoria temporalmente asignado
    URL.revokeObjectURL(url)
  }
  