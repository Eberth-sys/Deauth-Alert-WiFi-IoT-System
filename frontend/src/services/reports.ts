//frontend\src\services\reports.ts

// Función para obtener alertas en un rango de fechas específico
export const fetchAlertsByDate = async (start: string, end: string) => {
  // Realiza una petición GET al endpoint con parámetros de fecha
  const response = await fetch(
    `http://192.168.255.132:8000/custom-queries/alertas-por-fecha?start=${start}&end=${end}`
  )

  // Devuelve la respuesta parseada como JSON
  return await response.json()
}

// Función para obtener únicamente las alertas registradas hoy
export const fetchAlertsToday = async () => {
  // Realiza una petición GET al endpoint correspondiente
  const response = await fetch(`http://192.168.255.132:8000/custom-queries/alertas-de-hoy`)

  // Devuelve los resultados en formato JSON
  return await response.json()
}
