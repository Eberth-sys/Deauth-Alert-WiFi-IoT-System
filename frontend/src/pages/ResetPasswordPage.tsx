//frontend\src\pages\ResetPasswordPage.tsx

// -------------------- Importaciones --------------------
import { useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";     // Para extraer el token y redirigir
import PublicLayout from "./PublicLayout";                           // Layout visual para formularios públicos
import { resetPassword } from "../services/auth";                    // Función API para enviar nueva contraseña
import { validatePasswordStrength } from "../utils/validators";      // Valida requisitos mínimos de seguridad
import PasswordRequirements from "../components/PasswordRequirements"; // Muestra requisitos cumplidos
import PasswordInput from "../components/PasswordInput";             // opción de ver/ocultar contraseña

// -------------------- Componente: ResetPasswordPage --------------------
const ResetPasswordPage = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();                // Lee los parámetros de la URL
  const token = searchParams.get("token");                 // Extrae el token de recuperación

  // Estados del formulario
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  // -------------------- Envío del formulario --------------------
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setMessage("");

    if (!token) {
      setError("Token inválido o faltante.");
      return;
    }

    const pwdError = validatePasswordStrength(password);   // Valida requisitos
    if (pwdError) {
      setError("⚠️ " + pwdError);
      return;
    }

    if (password !== confirmPassword) {
      setError("⚠️ Las contraseñas no coinciden");
      return;
    }

    try {
      await resetPassword(token, password);                // Envío al backend
      setMessage("✅ Contraseña actualizada correctamente. Redirigiendo al login...");
      setTimeout(() => navigate("/login"), 3000);          // Redirige tras 3 segundos
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "❌ Error al actualizar la contraseña");
    }
  };

  // -------------------- Renderizado --------------------
  return (
    <PublicLayout>
      <form onSubmit={handleSubmit} className="space-y-4">
        <h2 className="text-lg font-semibold text-center text-blue-300">Restablecer contraseña</h2>
        <p className="text-sm text-gray-400 text-center">
          Ingresa una nueva contraseña segura para tu cuenta.
        </p>

        {/* Campo: Nueva contraseña */}
        <div>
          <label className="block text-sm font-medium">Nueva contraseña</label>
          <PasswordInput
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          {password && <PasswordRequirements password={password} />}
        </div>

        {/* Campo: Confirmación de contraseña */}
        <div>
          <label className="block text-sm font-medium">Confirmar contraseña</label>
          <PasswordInput
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
          />
        </div>

        {/* Mensajes de error o éxito */}
        {error && <div className="text-red-400 text-sm">{error}</div>}
        {message && <div className="text-green-400 text-sm">{message}</div>}

        {/* Botón de envío */}
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
