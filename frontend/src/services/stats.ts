//frontend\src\services\stats.ts

export const fetchTotalAlerts = async () => {
    const res = await fetch('http://192.168.255.132:8000/custom-queries/total-alertas')
    return await res.json()
  }
  
  export const fetchAlertsByNode = async () => {
    const res = await fetch('http://192.168.255.132:8000/custom-queries/alertas-por-nodo')
    return await res.json()
  }
  
  export const fetchAlertsByChannel = async () => {
    const res = await fetch('http://192.168.255.132:8000/custom-queries/canales-mas-afectados')
    return await res.json()
  }
  
  export const fetchLatestAlerts = async () => {
    const res = await fetch('http://192.168.255.132:8000/custom-queries/ultimas-alertas')
    return await res.json()
  }
  