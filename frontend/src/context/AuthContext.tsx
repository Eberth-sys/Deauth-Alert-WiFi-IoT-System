//frontend\src\context\AuthContext.tsx

// -------------------- Importaciones --------------------
import { createContext, useContext, ReactNode } from "react";  // React y tipos necesarios para contexto
import { useAuth } from "../hooks/useAuth";                    // Hook personalizado que maneja lógica de autenticación

// -------------------- Definición del tipo del contexto --------------------
interface AuthContextType {
  user: any;                                                             // Usuario autenticado (puede mejorarse con un tipo específico)
  login: (email: string, password: string) => Promise<void>;             // Función para iniciar sesión
  register: (username: string, email: string, password: string) => Promise<any>; // Función para registrar nuevo usuario
  logout: () => void;                                                    // Función para cerrar sesión
  getToken: () => string | null;                                         // Devuelve el token JWT actual
  isAuthenticated: boolean;                                              // true si hay sesión activa
  loading: boolean;                                                      // true si aún se está cargando el estado del usuario
}

// -------------------- Creación del contexto --------------------
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// -------------------- Hook para acceder al contexto fácilmente --------------------
export const useAuthContext = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuthContext debe usarse dentro de AuthProvider"); // Asegura uso correcto
  }
  return context;
};

// -------------------- Provider global que envuelve toda la app --------------------
export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const auth = useAuth();  // Ejecuta el hook con toda la lógica de autenticación (login, logout, etc.)

  return (
    <AuthContext.Provider value={auth}>  {/* Expone el estado y funciones del hook a toda la app */}
      {children}
    </AuthContext.Provider>
  );
};
