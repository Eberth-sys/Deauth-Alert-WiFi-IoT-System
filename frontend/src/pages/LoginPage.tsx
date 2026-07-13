//frontend\src\pages\LoginPage.tsx

// -------------------- Importaciones --------------------
import { useState } from "react";
import { useNavigate } from "react-router-dom";            // Para redirigir al dashboard tras login
import PublicLayout from "./PublicLayout";                 // Layout visual para páginas públicas
import { useAuthContext } from "../context/AuthContext";   // Hook de sesión global
import PasswordInput from "../components/PasswordInput";   // Campo de contraseña con visibilidad opcional

// -------------------- Componente: LoginPage --------------------
const LoginPage = () => {
  const { login } = useAuthContext();                      // Función login desde el contexto
  const navigate = useNavigate();                          // Redirección tras éxito

  // -------------------- Estados locales --------------------
  const [email, setEmail] = useState("");                  // Correo electrónico
  const [password, setPassword] = useState("");            // Contraseña
  const [error, setError] = useState("");                  // Mensaje de error

  // -------------------- Envío del formulario --------------------
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();                                    // Previene recarga
    setError("");                                          // Limpia error previo

    try {
      await login(email, password);                        // Intenta autenticación
      navigate("/");                                       // Redirige al dashboard
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "❌ Error al iniciar sesión");
    }
  };

  // -------------------- Renderizado --------------------
  return (
    <PublicLayout>
      <form onSubmit={handleSubmit} className="space-y-6 animate-fadeIn">
        
        {/* Campo: Correo electrónico */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-1">
            📧 Correo electrónico
          </label>
          <input
            type="email"
            className="w-full px-4 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-cyan-500 transition"
            placeholder="ejemplo@correo.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>

        {/* Campo: Contraseña con visibilidad opcional */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-1">
            🔒 Contraseña
          </label>
          <PasswordInput
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>

        {/* Mensaje de error si lo hay */}
        {error && (
          <div className="text-sm text-red-400 font-semibold animate-pulse text-center">
            {error}
          </div>
        )}

        {/* Botón de inicio de sesión */}
        <button
          type="submit"
          className="w-full py-2 bg-gradient-to-r from-cyan-500 to-blue-600 text-white rounded-lg font-semibold text-sm shadow hover:scale-[1.02] transition-all"
        >
          Iniciar sesión
        </button>

        {/* Enlaces: registro y recuperación */}
        <div className="text-sm text-center text-gray-400 space-y-1">
          <p>
            ¿No tienes cuenta?{" "}
            <a href="/register" className="text-cyan-400 hover:underline font-medium">
              Regístrate aquí
            </a>
          </p>
          <p>
            ¿Olvidaste tu contraseña?{" "}
            <a href="/forgot-password" className="text-blue-400 hover:underline font-medium">
              Recupérala aquí
            </a>
          </p>
        </div>
      </form>
    </PublicLayout>
  );
};

export default LoginPage;
