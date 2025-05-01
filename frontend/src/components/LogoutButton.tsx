//frontend\src\components\LogoutButton.tsx

// -------------------- Importaciones --------------------
import { useAuthContext } from "../context/AuthContext";  // Hook para acceder al contexto de autenticación
import { useNavigate } from "react-router-dom";           // Hook para redireccionar después de cerrar sesión

// -------------------- Componente: LogoutButton --------------------
const LogoutButton = () => {
  const { logout } = useAuthContext();                   // Función de cierre de sesión del contexto
  const navigate = useNavigate();                         // Función para redirigir al login tras cerrar sesión

  // -------------------- Manejo del cierre de sesión --------------------
  const handleLogout = () => {
    logout();                                            // Ejecuta el logout
    navigate("/login");                                   // Redirige al login después de cerrar sesión
  };

  return (
    <>
      {/* ✅ Escritorio: solo botón visible en la parte inferior derecha */}
      <div className="hidden sm:flex fixed bottom-4 right-6 z-50">
        <button
          onClick={handleLogout}
          className="px-4 py-2 rounded-full text-sm font-semibold text-white 
                     bg-gradient-to-r from-red-500 to-red-700 shadow-md 
                     hover:shadow-red-500/40 transition-all duration-300 
                     hover:scale-105"
        >
          🔓 Cerrar sesión
        </button>
      </div>
    </>
  );
};

export default LogoutButton;
