//frontend\src\services\reports.ts

export const fetchAlertsByDate = async (start: string, end: string) => {
    const response = await fetch(
      `http://192.168.255.132:8000/custom-queries/alertas-por-fecha?start=${start}&end=${end}`
    )
    return await response.json()
  }
  
  export const fetchAlertsToday = async () => {
    const response = await fetch(`http://192.168.255.132:8000/custom-queries/alertas-de-hoy`)
    return await response.json()
  }
  