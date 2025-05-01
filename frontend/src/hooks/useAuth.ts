// src/hooks/useAuth.ts

// -------------------- Importaciones --------------------
import { useState, useEffect } from "react";                            // Hooks de React
import { loginUser, registerUser, getProfile } from "../services/auth"; // Funciones del servicio de autenticación

// -------------------- Clave del token en localStorage --------------------
const TOKEN_KEY = "auth_token";

// -------------------- Hook personalizado: useAuth --------------------
export const useAuth = () => {
  const [user, setUser] = useState<any | null>(null);                  // Estado para el usuario autenticado
  const [loading, setLoading] = useState(true);                        // Estado para controlar la carga inicial

  // -------------------- Al iniciar la app, valida el token (si existe) --------------------
  useEffect(() => {
    const token = localStorage.getItem(TOKEN_KEY);                     // Busca el token almacenado

    const initSession = async () => {
      if (token) {
        try {
          const profile = await getProfile(token);                     // Intenta obtener perfil con el token
          setUser(profile);                                            // Si funciona, guarda el usuario
        } catch {
          logout();                                                    // Si el token no es válido, borra sesión
        }
      }
      setLoading(false);                                               // Marca que terminó la carga
    };

    initSession();
  }, []);

  // -------------------- Iniciar sesión --------------------
  const login = async (email: string, password: string) => {
    const data = await loginUser(email, password);                     // Llama a la API para obtener token
    localStorage.setItem(TOKEN_KEY, data.access_token);                // Guarda el token en el navegador
    const profile = await getProfile(data.access_token);               // Carga el perfil
    setUser(profile);                                                  // Actualiza el estado
  };

  // -------------------- Registrar usuario --------------------
  const register = async (username: string, email: string, password: string) => {
    const newUser = await registerUser(username, email, password);     // Llama a la API de registro
    return newUser;                                                    // Devuelve el nuevo usuario (puede usarse para confirmar)
  };

  // -------------------- Cerrar sesión --------------------
  const logout = () => {
    localStorage.removeItem(TOKEN_KEY);                                // Elimina el token
    setUser(null);                                                     // Limpia el usuario
  };

  // -------------------- Obtener token actual --------------------
  const getToken = () => localStorage.getItem(TOKEN_KEY);              // Devuelve el token actual desde el navegador

  // -------------------- Valores devueltos por el hook --------------------
  return {
    user,                  // Usuario actual
    loading,               // true si se está validando sesión
    login,                 // Función para login
    register,              // Función para registro
    logout,                // Función para logout
    getToken,              // Función para obtener token
    isAuthenticated: !!user // true si hay sesión activa
  };
};
