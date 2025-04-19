// frontend/src/services/socket.ts

// Variable global para almacenar el timeout en caso de reconexión automática
let reconnectTimeout: ReturnType<typeof setTimeout> | null = null

/**
 * Función para crear y gestionar la conexión WebSocket con el backend
 *
 * @param onMessage - Función callback que se ejecuta cuando se recibe un mensaje
 * @param onError - Función opcional para manejar errores
 * @param setConnectionStatus - Función opcional para actualizar estado visual de conexión
 * @returns WebSocket - Instancia del WebSocket conectado
 */
export const connectToWebSocket = (
  onMessage: (data: any) => void,
  onError?: (err: any) => void,
  setConnectionStatus?: (status: 'connected' | 'disconnected' | 'reconnecting') => void
): WebSocket => {

  // Crea una nueva conexión WebSocket hacia el backend
  const socket = new WebSocket('ws://192.168.255.132:8000/ws/alerts')

  // Evento: conexión exitosa
  socket.onopen = () => {
    console.log('🟢 WebSocket conectado')
    setConnectionStatus?.('connected') // Notifica estado "conectado"
  }

  // Evento: se recibe un mensaje del backend
  socket.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data) // Parsea el mensaje como JSON
      console.log('📨 Mensaje recibido del WebSocket:', data)
      onMessage(data) // Ejecuta callback con los datos
    } catch (e) {
      console.error('Error parseando el mensaje:', e)
    }
  }

  // Evento: ocurre un error en la conexión
  socket.onerror = (err) => {
    console.error('❌ WebSocket error:', err)
    setConnectionStatus?.('disconnected') // Actualiza estado visual
    if (onError) onError(err)             // Ejecuta callback de error si existe
  }

  // Evento: conexión cerrada (por error o por cierre manual)
  socket.onclose = () => {
    console.warn('🔌 WebSocket cerrado. Reintentando en 3s...')
    setConnectionStatus?.('reconnecting') // Notifica estado de reconexión

    // Si ya había un intento programado, lo cancela
    if (reconnectTimeout) clearTimeout(reconnectTimeout)

    // Intenta reconectar después de 3 segundos
    reconnectTimeout = setTimeout(() => {
      connectToWebSocket(onMessage, onError, setConnectionStatus)
    }, 3000)
  }

  return socket // Devuelve el socket conectado
}
