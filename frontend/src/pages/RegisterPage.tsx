//frontend\src\pages\RegisterPage.tsx

// -------------------- Importaciones --------------------
import { useState } from "react";                                  // Hook para manejar el estado local del formulario
import { useNavigate } from "react-router-dom";                    // Para redirigir después del registro
import PublicLayout from "./PublicLayout";                         // Layout visual reutilizable para páginas públicas
import { useAuthContext } from "../context/AuthContext";           // Hook de autenticación global
import { validatePasswordStrength } from "../utils/validators";    // Función que valida la fortaleza de la contraseña
import PasswordRequirements from "../components/PasswordRequirements"; // Componente visual para requisitos de la contraseña

// -------------------- Componente: RegisterPage --------------------
const RegisterPage = () => {
  const { register } = useAuthContext();                           // Función de registro desde el contexto
  const navigate = useNavigate();                                  // Para redirigir al login tras registro

  // -------------------- Estados del formulario --------------------
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");

  // -------------------- Envío del formulario --------------------
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    // Validar fortaleza de la contraseña
    const pwdError = validatePasswordStrength(password);
    if (pwdError) {
      setError("⚠️ " + pwdError);
      return;
    }

    // Validar coincidencia de contraseñas
    if (password !== confirmPassword) {
      setError("⚠️ Las contraseñas no coinciden");
      return;
    }

    // Intentar registrar al usuario
    try {
      await register(username, email, password);
      alert("✅ Registro exitoso. ¡Ahora inicia sesión!");
      navigate("/login");
    } catch (err: any) {
      setError(err.message || "❌ Error al registrarse");
    }
  };

  // -------------------- Renderizado --------------------
  return (
    <PublicLayout>
      <form onSubmit={handleSubmit} className="space-y-4">

        {/* Campo: Nombre de usuario */}
        <div>
          <label className="block text-sm font-medium">Nombre de usuario</label>
          <input
            type="text"
            className="w-full px-3 py-2 mt-1 bg-gray-700 border border-gray-600 rounded text-white"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
        </div>

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

        {/* Campo: Contraseña + validaciones visuales */}
        <div>
          <label className="block text-sm font-medium">Contraseña</label>
          <input
            type="password"
            className="w-full px-3 py-2 mt-1 bg-gray-700 border border-gray-600 rounded text-white"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          {password && <PasswordRequirements password={password} />} {/* Visualiza requisitos cumplidos */}
        </div>

        {/* Campo: Confirmación de contraseña */}
        <div>
          <label className="block text-sm font-medium">Confirmar contraseña</label>
          <input
            type="password"
            className="w-full px-3 py-2 mt-1 bg-gray-700 border border-gray-600 rounded text-white"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            required
          />
        </div>

        {/* Mensaje de error */}
        {error && (
          <div className="text-sm text-red-400 font-semibold animate-pulse">
            {error}
          </div>
        )}

        {/* Botón de envío */}
        <button
          type="submit"
          className="w-full bg-green-600 hover:bg-green-700 text-white py-2 rounded font-semibold transition duration-200"
        >
          Crear cuenta
        </button>

        {/* Enlace para volver al login */}
        <p className="text-sm text-center text-gray-400">
          ¿Ya tienes cuenta?{" "}
          <a href="/login" className="text-blue-400 hover:underline">
            Inicia sesión aquí
          </a>
        </p>
      </form>
    </PublicLayout>
  );
};

export default RegisterPage;
