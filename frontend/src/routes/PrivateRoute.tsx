//frontend\src\auth\PrivateRoute.tsx

// -------------------- Importaciones --------------------
import { Navigate } from "react-router-dom";               // Para redirigir si el usuario no está autenticado
import { useAuthContext } from "../context/AuthContext";   // Hook del contexto para acceder a la sesión
import { ReactElement } from "react";                      // Tipo necesario para definir correctamente el prop `children`

// -------------------- Componente: PrivateRoute --------------------
const PrivateRoute = ({ children }: { children: ReactElement }) => {
  const { isAuthenticated, loading } = useAuthContext();   // Extrae el estado de sesión y carga del contexto

  // Si aún se está validando el estado de autenticación
  if (loading) {
    return (
      <div className="h-screen flex items-center justify-center text-white font-bold text-lg">
        Cargando autenticación...
      </div>
    );
  }

  // Si está autenticado → renderiza el contenido
  // Si no está autenticado → redirige al login
  return isAuthenticated ? children : <Navigate to="/login" replace />;
};

export default PrivateRoute;
