//frontend\src\pages\RegisterPage.tsx

// -------------------- Importaciones --------------------
import { useState } from "react";
import { useNavigate } from "react-router-dom";                    // Para redireccionar tras el registro
import PublicLayout from "./PublicLayout";                         // Layout visual unificado para páginas públicas
import { useAuthContext } from "../context/AuthContext";           // Hook del contexto de autenticación
import { validatePasswordStrength } from "../utils/validators";    // Validador personalizado para contraseñas fuertes
import PasswordRequirements from "../components/PasswordRequirements"; // Componente visual de requisitos
import PasswordInput from "../components/PasswordInput";           // Input con visibilidad de contraseña

// -------------------- Componente: RegisterPage --------------------
const RegisterPage = () => {
  const { register } = useAuthContext();       // Accede a la función register del contexto
  const navigate = useNavigate();              // Hook para navegación posterior al registro

  // -------------------- Estados del formulario --------------------
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");

  // -------------------- Maneja el envío del formulario --------------------
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    const pwdError = validatePasswordStrength(password);       // Valida requisitos mínimos
    if (pwdError) {
      setError("⚠️ " + pwdError);
      return;
    }

    if (password !== confirmPassword) {
      setError("⚠️ Las contraseñas no coinciden");
      return;
    }

    try {
      await register(username, email, password);               // Intenta registrar al usuario
      alert("✅ Registro exitoso. ¡Ahora inicia sesión!");
      navigate("/login");                                      // Redirige al login tras éxito
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

        {/* Campo: Contraseña */}
        <div>
          <label className="block text-sm font-medium">Contraseña</label>
          <PasswordInput
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          {password && <PasswordRequirements password={password} />}  {/* Visualiza requisitos si hay texto */}
        </div>

        {/* Campo: Confirmación de contraseña */}
        <div>
          <label className="block text-sm font-medium">Confirmar contraseña</label>
          <PasswordInput
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
          />
        </div>

        {/* Mensaje de error */}
        {error && (
          <div className="text-sm text-red-400 font-semibold animate-pulse">
            {error}
          </div>
        )}

        {/* Botón de registro */}
        <button
          type="submit"
          className="w-full bg-green-600 hover:bg-green-700 text-white py-2 rounded font-semibold transition duration-200"
        >
          Crear cuenta
        </button>

        {/* Enlace a login */}
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
