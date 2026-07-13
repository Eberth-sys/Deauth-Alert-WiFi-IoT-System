//frontend\src\utils\validators.ts

// -------------------- Validación de fortaleza de contraseña --------------------
// Retorna un string con el error si la contraseña no es válida, o null si es segura
export const validatePasswordStrength = (password: string): string | null => {
    if (password.length < 8) return "Debe tener al menos 8 caracteres.";                                     // Verifica longitud mínima
    if (!/[A-Z]/.test(password)) return "Debe contener al menos una letra mayúscula.";                       // Verifica presencia de mayúscula
    if (!/[a-z]/.test(password)) return "Debe contener al menos una letra minúscula.";                       // Verifica presencia de minúscula
    if (!/[0-9]/.test(password)) return "Debe contener al menos un número.";                                 // Verifica presencia de número
    if (!/[!@#$%^&*()_+\-=[\]{};':"\\|,.<>/?]/.test(password)) return "Debe tener un carácter especial."; // Verifica presencia de símbolo
  
    const COMMON_PASSWORDS = [                                                                               // Lista de contraseñas comunes
      "123456", "password", "12345678", "qwerty",
      "admin123", "123456789", "admin", "abc123"
    ];
    if (COMMON_PASSWORDS.includes(password.toLowerCase())) return "La contraseña es demasiado común o insegura."; // Verifica si es común
  
    return null;                                                                                                 // Si pasa todas las validaciones
  };
  