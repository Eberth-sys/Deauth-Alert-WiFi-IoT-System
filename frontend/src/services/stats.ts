//frontend\src\services\stats.ts

// -------------------- Carga de URL del backend desde archivo .env --------------------
const API_URL = import.meta.env.VITE_BACKEND_URL || "http://localhost:8000";

/**
 * Obtiene el número total de alertas registradas en la base de datos.
 * Utiliza el endpoint: /custom-queries/total-alertas
 */
export const fetchTotalAlerts = async () => {
  const res = await fetch(`${API_URL}/custom-queries/total-alertas`);
  return await res.json();
};

/**
 * Obtiene el número de alertas agrupadas por nodo IoT.
 * Utiliza el endpoint: /custom-queries/alertas-por-nodo
 */
export const fetchAlertsByNode = async () => {
  const res = await fetch(`${API_URL}/custom-queries/alertas-por-nodo`);
  return await res.json();
};

/**
 * Obtiene el número de alertas agrupadas por canal WiFi.
 * Utiliza el endpoint: /custom-queries/canales-mas-afectados
 */
export const fetchAlertsByChannel = async () => {
  const res = await fetch(`${API_URL}/custom-queries/canales-mas-afectados`);
  return await res.json();
};

/**
 * Obtiene las 10 alertas más recientes registradas en la base de datos.
 * Utiliza el endpoint: /custom-queries/ultimas-alertas
 */
export const fetchLatestAlerts = async () => {
  const res = await fetch(`${API_URL}/custom-queries/ultimas-alertas`);
  return await res.json();
};
