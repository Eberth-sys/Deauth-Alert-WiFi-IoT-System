//frontend\src\components\PasswordInput.tsx

// -------------------- Importaciones --------------------
import { useState } from "react";
import { EyeIcon, EyeSlashIcon } from "@heroicons/react/24/outline"; // Iconos para mostrar/ocultar contraseña

// -------------------- Tipado de props --------------------
interface PasswordInputProps {
  value: string;                                                    // Valor actual del campo
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;       // Manejador de cambio
  placeholder?: string;                                             // Texto placeholder (opcional)
  name?: string;                                                    // Nombre del input (opcional)
  required?: boolean;                                               // Si el campo es obligatorio (default: true)
}

// -------------------- Componente: PasswordInput --------------------
const PasswordInput = ({
  value,
  onChange,
  placeholder = "••••••••",
  name = "password",
  required = true,
}: PasswordInputProps) => {
  const [showPassword, setShowPassword] = useState(false);         // Estado para mostrar u ocultar la contraseña

  return (
    <div className="relative group">
      {/* Campo de contraseña (con visibilidad controlada) */}
      <input
        type={showPassword ? "text" : "password"}                   // Alterna tipo de input
        name={name}
        placeholder={placeholder}
        value={value}
        onChange={onChange}
        required={required}
        className="w-full px-4 py-2 pr-12 bg-gray-900 border border-gray-700 rounded-lg text-white placeholder-gray-500
          focus:outline-none focus:ring-2 focus:ring-cyan-500 transition-all duration-200 shadow-sm"
      />

      {/* Icono interactivo para alternar visibilidad, solo si hay texto */}
      {value.length > 0 && (
        <button
          type="button"
          onClick={() => setShowPassword((prev) => !prev)}
          aria-label={showPassword ? "Ocultar contraseña" : "Mostrar contraseña"}
          className="absolute right-2.5 top-1/2 -translate-y-1/2 p-1.5 rounded-md bg-gray-800/70 border border-gray-600 shadow
                    hover:bg-cyan-600 hover:text-white text-cyan-300 transition-all duration-200"
        >
          {showPassword ? (
            <EyeSlashIcon className="w-4 h-4" />
          ) : (
            <EyeIcon className="w-4 h-4" />
          )}
        </button>
      )}

    </div>
  );
};

export default PasswordInput;
