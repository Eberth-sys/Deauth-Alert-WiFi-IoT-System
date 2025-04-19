//frontend\src\components\ConnectionNotification.tsx


import React from 'react'
import AlertNotification from './AlertNotification'

interface Props {
  message: string
  onClose: () => void
}

const ConnectionNotification: React.FC<Props> = ({ message, onClose }) => {
  return (
    <AlertNotification
      message={message}
      onClose={onClose}
      sound="/sounds/notification.mp3" // sonido específico para cambios de conexión
    />
  )
}

export default ConnectionNotification
