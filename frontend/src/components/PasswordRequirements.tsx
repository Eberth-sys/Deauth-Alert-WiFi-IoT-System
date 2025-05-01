//frontend\src\components\PasswordRequirements.tsx

// -------------------- Componente: PasswordRequirements --------------------
// Recibe una contraseña y muestra visualmente si cumple ciertos requisitos
const PasswordRequirements = ({ password }: { password: string }) => {
    // Lista de validaciones a aplicar a la contraseña
    const checks = [
      { test: password.length >= 8, label: "Mínimo 8 caracteres" },
      { test: /[A-Z]/.test(password), label: "Una letra mayúscula" },
      { test: /[a-z]/.test(password), label: "Una letra minúscula" },
      { test: /[0-9]/.test(password), label: "Un número" },
      { test: /[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]/.test(password), label: "Un carácter especial" },
    ];
  
    // -------------------- Renderizado --------------------
    return (
      <div className="bg-gray-800 text-sm p-3 rounded shadow-lg border border-gray-700 mt-2 space-y-1">
        {checks.map((check, idx) => (
          <div key={idx} className="flex items-center gap-2">
            <span className={check.test ? "text-green-400" : "text-red-400"}>
              {check.test ? "✅" : "❌"} {/* Muestra ícono según resultado */}
            </span>
            <span className="text-gray-300">{check.label}</span> {/* Texto descriptivo */}
          </div>
        ))}
      </div>
    );
  };
  
  export default PasswordRequirements;
  
  