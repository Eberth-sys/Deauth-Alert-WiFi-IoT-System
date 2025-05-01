//frontend\src\pages\ForgotPasswordPage.tsx

// -------------------- Importaciones --------------------
import { useState } from "react";                          // Hook para manejar estados locales
import { requestPasswordReset } from "../services/auth";   // Función del servicio para solicitar enlace de recuperación
import PublicLayout from "./PublicLayout";                 // Layout reutilizable para páginas públicas

// -------------------- Componente: ForgotPasswordPage --------------------
const ForgotPasswordPage = () => {
  const [email, setEmail] = useState("");                  // Estado del campo de correo
  const [message, setMessage] = useState("");              // Estado para mensaje de éxito
  const [error, setError] = useState("");                  // Estado para mensaje de error

  // -------------------- Maneja el envío del formulario --------------------
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setMessage("");
    setError("");

    try {
      const res = await requestPasswordReset(email);       // Envía la solicitud al backend
      setMessage("✅ Se envió un enlace de recuperación a tu correo.");
    } catch (err: any) {
      setError("❌ " + (err.message || "Error al enviar recuperación")); // Muestra error si falla
    }
  };

  // -------------------- Renderizado --------------------
  return (
    <PublicLayout>
      <form onSubmit={handleSubmit} className="space-y-4">
        <h2 className="text-lg font-semibold text-center text-blue-300">
          Recuperar contraseña
        </h2>
        <p className="text-sm text-gray-400 text-center">
          Ingresa tu correo electrónico para recibir un enlace de restablecimiento.
        </p>

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

        {/* Mensajes de éxito o error */}
        {message && <div className="text-green-400 text-sm">{message}</div>}
        {error && <div className="text-red-400 text-sm">{error}</div>}

        {/* Botón de envío */}
        <button
          type="submit"
          className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 rounded font-semibold transition"
        >
          Enviar enlace de recuperación
        </button>

        {/* Enlace para volver al login */}
        <p className="text-sm text-center text-gray-400 mt-4">
          ¿Recordaste tu contraseña?{" "}
          <a href="/login" className="text-blue-400 hover:underline">
            Volver a login
          </a>
        </p>
      </form>
    </PublicLayout>
  );
};

export default ForgotPasswordPage;
