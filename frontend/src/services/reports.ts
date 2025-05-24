//frontend\src\services\reports.ts

// -------------------- URL base del backend (desde .env) --------------------
const API_URL = import.meta.env.VITE_BACKEND_URL || "http://localhost:8000";  // Valor por defecto si no está definido

// -------------------- Función: Obtener alertas en un rango de fechas --------------------
export const fetchAlertsByDate = async (start: string, end: string) => {
  /**
   * Realiza una petición GET al backend para obtener alertas
   * entre dos fechas específicas, utilizando parámetros en la URL.
   */
  const response = await fetch(
    `${API_URL}/custom-queries/alertas-por-fecha?start=${start}&end=${end}`
  );

  // Devuelve la respuesta en formato JSON
  return await response.json();
};

// -------------------- Función: Obtener alertas registradas hoy --------------------
export const fetchAlertsToday = async () => {
  /**
   * Realiza una petición GET al backend para obtener todas las alertas
   * registradas durante el día actual.
   */
  const response = await fetch(`${API_URL}/custom-queries/alertas-de-hoy`);

  // Devuelve la respuesta parseada como JSON
  return await response.json();
};
