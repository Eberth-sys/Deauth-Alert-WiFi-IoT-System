// frontend/src/components/utils/logs.ts

// -------------------- URL base del backend (desde archivo .env) --------------------
const API_URL = import.meta.env.VITE_BACKEND_URL || "http://localhost:8000";

/**
 * Solicita al backend el contenido de un archivo de logs específico.
 * @param filename - Nombre del archivo de logs (por ejemplo: ble_events.log)
 * @returns Un arreglo con cada línea del log como string
 */
export const fetchLogFile = async (filename: string): Promise<string[]> => {
  const response = await fetch(`${API_URL}/logs/${filename}`); // Llama al endpoint usando la URL desde .env
  const data = await response.json();
  return data.content; // Retorna el contenido del log
};

/**
 * Descarga el contenido del log como archivo .txt desde el navegador.
 * @param filename - Nombre del archivo a descargar
 * @param lines - Contenido del archivo (una línea por elemento del array)
 */
export const downloadLogFile = (filename: string, lines: string[]) => {
  const blob = new Blob([lines.join('\n')], { type: 'text/plain' }); // Crea un blob de texto plano
  const url = URL.createObjectURL(blob); // Genera una URL temporal para descarga
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click(); // Dispara la descarga
  document.body.removeChild(link);
  URL.revokeObjectURL(url); // Libera el recurso temporal
};

/**
 * Asigna un color CSS según el tipo de línea del log.
 * @param line - Línea del log (texto)
 * @returns Clase de color para aplicar en el frontend
 */
export const getLineColor = (line: string): string => {
  if (line.includes('ERROR')) return 'text-red-400';
  if (line.includes('WARNING')) return 'text-yellow-400';
  if (line.includes('CRITICAL')) return 'text-pink-400 font-bold';
  if (line.includes('INFO')) return 'text-green-400';
  return 'text-white'; // Línea sin categoría especial
};
