// frontend\src\components\utils\download.ts

export const downloadCSV = (data: any[], filename: string) => {
    if (!data.length) return
  
    const headers = Object.keys(data[0])
    const csvRows = [
      headers.join(','), // encabezado
      ...data.map((row) =>
        headers.map((field) => JSON.stringify(row[field], (_, v) => v ?? '')).join(',')
      )
    ]
  
    const blob = new Blob([csvRows.join('\n')], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
  
    const a = document.createElement('a')
    a.href = url
    a.download = `${filename}.csv`
    a.click()
  
    URL.revokeObjectURL(url)
  }
  