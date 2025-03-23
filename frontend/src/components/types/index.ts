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
  