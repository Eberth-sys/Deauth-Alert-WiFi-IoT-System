//frontend\src\components\types\index.ts

export type AlertSummary = {
    canal: number
    count: number
    last_seen: string | null
    nodo_iot: string
    spoofed_bssid: string
    target_mac: string
  }
  
  export type NodeStatus = {
    device_name: string
    mac_address: string
    status: 'connected' | 'disconnected'
    last_update: string
  }
  
  export type AggregatedAlert = {
    nodo_iot: string
    canal: number
    count: number
    lastSeen: string
    spoofed_bssid: string
    target_mac: string
    isConnected: boolean
    lastConnection: string
  }

// -------------------- Evento de alerta (por-evento) --------------------
// Tipo de evento 802.11 detectado (F2, DEC-0003).
export type EventType = 'deauth' | 'disassoc'

// Alerta individual tal como la devuelve el backend (AlertResponse / SELECT * FROM alerts).
export type AlertEvent = {
  id: number
  nodo_iot: string
  spoofed_bssid: string
  target_mac: string
  bssid: string
  canal: number
  event_type: EventType
  timestamp: string
}
