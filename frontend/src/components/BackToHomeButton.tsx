// frontend/src/components/BackToHomeButton.tsx
import { Link } from 'react-router-dom'

const BackToHomeButton = () => {
  return (
    <Link
      to="/"
      className="text-white font-bold text-lg flex items-center gap-2 hover:text-blue-400 transition"
    >
      <span className="text-xl">🏠</span>
      <span className="text-sm sm:text-base">Volver al Inicio</span>
    </Link>
  )
}

export default BackToHomeButton
