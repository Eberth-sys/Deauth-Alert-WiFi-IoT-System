//frontend\src\components\LogoutButton.tsx

// -------------------- Importaciones --------------------
import { useAuthContext } from "../context/AuthContext";  // Hook de autenticación para acceder a logout y user
import { useNavigate } from "react-router-dom";           // Hook para redirección después del logout

// -------------------- Componente: LogoutButton --------------------
const LogoutButton = () => {
  const { logout, user } = useAuthContext();              // Accede al usuario actual y función logout
  const navigate = useNavigate();                         // Permite redirigir al login

  // -------------------- Manejador de cierre de sesión --------------------
  const handleLogout = () => {
    logout();                                             // Limpia sesión y token
    navigate("/login");                                   // Redirige al login
  };

  return (
    <>
      {/* -------------------- Versión escritorio (top-right) -------------------- */}
      <div className="absolute top-4 right-4 hidden sm:flex items-center gap-4">
        <span className="text-sm text-gray-400 truncate max-w-[140px]">
          👤 {user?.username}                              {/* Muestra el nombre del usuario */}
        </span>
        <button
          onClick={handleLogout}
          className="px-4 py-2 rounded-lg text-sm font-semibold text-white bg-gradient-to-r from-red-500 to-red-700 shadow-md hover:shadow-red-500/40 transition-all duration-300 hover:scale-105 hover:animate-pulse"
        >
          🔓 Cerrar sesión
        </button>
      </div>

      {/* -------------------- Versión móvil (bottom-right) -------------------- */}
      <div className="fixed bottom-4 right-4 sm:hidden z-50 animate-bounce">
        <button
          onClick={handleLogout}
          title="Cerrar sesión"
          className="flex items-center gap-2 bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-full shadow-lg text-sm font-semibold transition-all duration-300 hover:scale-105"
        >
          🔓
          <span>Cerrar</span>
        </button>
      </div>
    </>
  );
};

export default LogoutButton;
