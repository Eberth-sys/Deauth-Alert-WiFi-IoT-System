// frontend/src/services/socket.ts

let reconnectTimeout: ReturnType<typeof setTimeout> | null = null

export const connectToWebSocket = (
  onMessage: (data: any) => void,
  onError?: (err: any) => void,
  setConnectionStatus?: (status: 'connected' | 'disconnected' | 'reconnecting') => void
): WebSocket => {
  const socket = new WebSocket('ws://192.168.255.128:8000/ws/alerts')

  socket.onopen = () => {
    console.log('🟢 WebSocket conectado')
    setConnectionStatus?.('connected')
  }

  socket.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      console.log('📨 Mensaje recibido del WebSocket:', data)
      onMessage(data)
    } catch (e) {
      console.error('Error parseando el mensaje:', e)
    }
  }

  socket.onerror = (err) => {
    console.error('❌ WebSocket error:', err)
    setConnectionStatus?.('disconnected')
    if (onError) onError(err)
  }

  socket.onclose = () => {
    console.warn('🔌 WebSocket cerrado. Reintentando en 3s...')
    setConnectionStatus?.('reconnecting')
    if (reconnectTimeout) clearTimeout(reconnectTimeout)
    reconnectTimeout = setTimeout(() => {
      connectToWebSocket(onMessage, onError, setConnectionStatus)
    }, 3000)
  }

  return socket
}
