// frontend/src/components/utils/formatters.ts

// Importamos dayjs para manipular fechas y su localización
import dayjs from 'dayjs'
import 'dayjs/locale/es' // Localización en español
import localizedFormat from 'dayjs/plugin/localizedFormat' // Formato más amigable
import type { EventType } from '../types' // Tipo de evento (F2)

// Aplicamos las configuraciones a dayjs
dayjs.extend(localizedFormat)
dayjs.locale('es')

/**
 * Formatea una cadena de fecha en formato amigable
 * @param dateStr - Fecha a formatear (puede ser null o "-")
 * @returns Fecha formateada en español o "-" si no es válida
 */
export const formatDate = (dateStr: string | null): string => {
  if (!dateStr || dateStr === '-') return '-'
  return dayjs(dateStr).format('D [de] MMMM [de] YYYY, h:mm:ss A')
}

/**
 * Devuelve una clase CSS tipo heatmap según la cantidad de alertas
 * @param count - Número de alertas
 * @returns Clase de fondo y texto para resaltar gravedad
 */
export const getHeatColor = (count: number): string => {
  if (count >= 100) return 'bg-red-600 text-white'      // Crítico
  if (count >= 50) return 'bg-orange-500 text-white'    // Alto
  if (count >= 10) return 'bg-yellow-400 text-black'    // Medio
  return 'bg-green-400 text-black'                      // Bajo
}

/**
 * Devuelve una clase CSS basada en si el nodo está conectado
 * @param isConnected - Estado booleano de conexión
 * @returns Clase de color para texto
 */
export const getConnectionStatusStyle = (isConnected: boolean): string =>
  isConnected ? 'text-green-400' : 'text-red-400'

/**
 * Devuelve el texto correspondiente al estado de conexión
 * @param isConnected - Estado booleano
 * @returns Texto "Conectado" o "Desconectado"
 */
export const getConnectionStatusText = (isConnected: boolean): string =>
  isConnected ? 'Conectado' : 'Desconectado'

/**
 * Devuelve una clase CSS para el color del indicador de alerta
 * @param count - Número de alertas
 * @returns Color según si hay alerta o no
 */
export const getAlertIndicatorColor = (count: number): string =>
  count > 0 ? 'bg-red-500' : 'bg-green-500'

/**
 * Devuelve texto del estado según número de alertas
 * @param count - Número de alertas
 * @returns "Alerta" si hay alertas, "Ok" si no
 */
export const getAlertIndicatorText = (count: number): string =>
  count > 0 ? 'Alerta' : 'Ok'

/**
 * Devuelve la etiqueta y las clases para el badge del tipo de evento (F2).
 * El significado lo transmite el texto (label); el color es secundario
 * (no depende únicamente del color).
 * @param event_type - 'deauth' | 'disassoc'
 * @returns { label, className }
 */
export const getEventTypeBadge = (
  event_type: EventType
): { label: string; className: string } => {
  const base = 'text-xs font-semibold px-2 py-1 rounded-full whitespace-nowrap'
  if (event_type === 'disassoc') {
    return { label: 'Desasociación', className: `${base} bg-amber-500/20 text-amber-300 ring-1 ring-amber-500/40` }
  }
  return { label: 'Desautenticación', className: `${base} bg-red-500/20 text-red-300 ring-1 ring-red-500/40` }
}
