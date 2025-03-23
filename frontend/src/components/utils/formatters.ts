//frontend\src\components\utils\formatters.ts

import dayjs from 'dayjs'
import 'dayjs/locale/es'
import localizedFormat from 'dayjs/plugin/localizedFormat'

dayjs.extend(localizedFormat)
dayjs.locale('es')

export const formatDate = (dateStr: string | null): string => {
  if (!dateStr || dateStr === '-') return '-'
  return dayjs(dateStr).format('D [de] MMMM [de] YYYY, h:mm:ss A')
}

export const getHeatColor = (count: number): string => {
  if (count >= 100) return 'bg-red-600 text-white'
  if (count >= 50) return 'bg-orange-500 text-white'
  if (count >= 10) return 'bg-yellow-400 text-black'
  return 'bg-green-400 text-black'
}

export const getConnectionStatusStyle = (isConnected: boolean): string =>
  isConnected ? 'text-green-400' : 'text-red-400'

export const getConnectionStatusText = (isConnected: boolean): string =>
  isConnected ? 'Conectado' : 'Desconectado'

export const getAlertIndicatorColor = (count: number): string =>
  count > 0 ? 'bg-red-500' : 'bg-green-500'

export const getAlertIndicatorText = (count: number): string =>
  count > 0 ? 'Alerta' : 'Ok'
