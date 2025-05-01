//frontend\src\pages\LoginPage.tsx

// -------------------- Importaciones --------------------
import { useState } from "react";                        // Hook para manejar estados del formulario
import { useNavigate } from "react-router-dom";          // Para redirigir al usuario después del login
import PublicLayout from "./PublicLayout";               // Layout común para páginas públicas
import { useAuthContext } from "../context/AuthContext"; // Hook personalizado con acceso al contexto de autenticación

// -------------------- Componente: LoginPage --------------------
const LoginPage = () => {
  const { login } = useAuthContext();                    // Función login desde el contexto global
  const navigate = useNavigate();                        // Permite redirigir luego de autenticarse

  // -------------------- Estados locales del formulario --------------------
  const [email, setEmail] = useState("");                // Campo: email
  const [password, setPassword] = useState("");          // Campo: contraseña
  const [error, setError] = useState("");                // Mensaje de error en caso de fallo

  // -------------------- Manejador del formulario --------------------
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();                                  // Previene recarga de la página
    setError("");                                         // Limpia errores anteriores

    try {
      await login(email, password);                      // Intenta autenticar
      navigate("/");                                     // Si tiene éxito, redirige al dashboard
    } catch (err: any) {
      setError(err.message || "❌ Error al iniciar sesión"); // Si falla, muestra mensaje de error
    }
  };

  // -------------------- Renderizado --------------------
  return (
    <PublicLayout>
      <form onSubmit={handleSubmit} className="space-y-4">

        {/* Campo: Correo electrónico */}
        <div>
          <label className="block text-sm font-medium">Correo electrónico</label>
          <input
            type="email"
            className="w-full px-3 py-2 mt-1 bg-gray-700 border border-gray-600 rounded text-white"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>

        {/* Campo: Contraseña */}
        <div>
          <label className="block text-sm font-medium">Contraseña</label>
          <input
            type="password"
            className="w-full px-3 py-2 mt-1 bg-gray-700 border border-gray-600 rounded text-white"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>

        {/* Mensaje de error si ocurre un fallo */}
        {error && (
          <div className="text-sm text-red-400 font-semibold animate-pulse">
            {error}
          </div>
        )}

        {/* Botón: Iniciar sesión */}
        <button
          type="submit"
          className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 rounded font-semibold transition duration-200"
        >
          Iniciar sesión
        </button>

        {/* Enlace: Registro */}
        <p className="text-sm text-center text-gray-400">
          ¿No tienes cuenta?{" "}
          <a href="/register" className="text-blue-400 hover:underline">
            Regístrate aquí
          </a>
        </p>

        {/* Enlace: Recuperar contraseña */}
        <p className="text-sm text-center text-gray-400">
          ¿Olvidaste tu contraseña?{" "}
          <a href="/forgot-password" className="text-blue-400 hover:underline">
            Recupérala aquí
          </a>
        </p>
      </form>
    </PublicLayout>
  );
};

export default LoginPage;
