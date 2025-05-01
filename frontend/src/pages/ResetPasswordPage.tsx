//frontend\src\pages\ResetPasswordPage.tsx

// -------------------- Importaciones --------------------
import { useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";  // Para obtener el token de la URL y redirigir
import PublicLayout from "./PublicLayout";                        // Layout para páginas públicas
import { resetPassword } from "../services/auth";                 // Función para enviar la nueva contraseña al backend
import { validatePasswordStrength } from "../utils/validators";   // Valida si la contraseña es segura
import PasswordRequirements from "../components/PasswordRequirements"; // Muestra los requisitos de la contraseña

// -------------------- Componente: ResetPasswordPage --------------------
const ResetPasswordPage = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();            // Obtiene los parámetros de la URL
  const token = searchParams.get("token");             // Extrae el token de recuperación

  // -------------------- Estados del formulario --------------------
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  // -------------------- Maneja el envío del formulario --------------------
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setMessage("");

    // Verifica que el token esté presente
    if (!token) {
      setError("Token inválido o faltante.");
      return;
    }

    // Verifica fortaleza de contraseña
    const pwdError = validatePasswordStrength(password);
    if (pwdError) {
      setError("⚠️ " + pwdError);
      return;
    }

    // Verifica coincidencia de ambas contraseñas
    if (password !== confirmPassword) {
      setError("⚠️ Las contraseñas no coinciden");
      return;
    }

    // Envía la nueva contraseña al backend
    try {
      await resetPassword(token, password);
      setMessage("✅ Contraseña actualizada correctamente. Redirigiendo al login...");
      setTimeout(() => navigate("/login"), 3000);  // Redirige luego de 3 segundos
    } catch (err: any) {
      setError(err.message || "❌ Error al actualizar la contraseña");
    }
  };

  // -------------------- Renderizado --------------------
  return (
    <PublicLayout>
      <form onSubmit={handleSubmit} className="space-y-4">
        <h2 className="text-lg font-semibold text-center text-blue-300">
          Restablecer contraseña
        </h2>
        <p className="text-sm text-gray-400 text-center">
          Ingresa una nueva contraseña segura para tu cuenta.
        </p>

        {/* Campo: Nueva contraseña */}
        <div>
          <label className="block text-sm font-medium">Nueva contraseña</label>
          <input
            type="password"
            className="w-full px-3 py-2 mt-1 bg-gray-700 border border-gray-600 rounded text-white"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          {password && <PasswordRequirements password={password} />}
        </div>

        {/* Campo: Confirmar contraseña */}
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

        {/* Mensajes de error o éxito */}
        {error && <div className="text-red-400 text-sm">{error}</div>}
        {message && <div className="text-green-400 text-sm">{message}</div>}

        {/* Botón: Actualizar contraseña */}
        <button
          type="submit"
          className="w-full bg-green-600 hover:bg-green-700 text-white py-2 rounded font-semibold transition"
        >
          Actualizar contraseña
        </button>
      </form>
    </PublicLayout>
  );
};

export default ResetPasswordPage;
