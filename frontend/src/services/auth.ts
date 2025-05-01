//frontend\src\services\auth.ts

// -------------------- URL base del backend --------------------
const API_URL = "http://192.168.255.132:8000";  // Recomendación: mover a archivo .env en producción

// -------------------- Iniciar sesión --------------------
export const loginUser = async (email: string, password: string) => {
  const res = await fetch(`${API_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),                // Envia las credenciales en formato JSON
  });

  if (!res.ok) throw new Error("❌ Credenciales inválidas");

  return await res.json();  // Devuelve: { access_token, token_type }
};

// -------------------- Registrar nuevo usuario --------------------
export const registerUser = async (
  username: string,
  email: string,
  password: string
) => {
  const res = await fetch(`${API_URL}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, email, password }),      // Datos del nuevo usuario
  });

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "❌ Registro fallido");
  }

  return await res.json();  // Devuelve: { id, username, email, ... }
};

// -------------------- Obtener perfil del usuario autenticado --------------------
export const getProfile = async (token: string) => {
  const res = await fetch(`${API_URL}/auth/me`, {
    headers: { Authorization: `Bearer ${token}` },            // Se envía el token JWT en el header
  });

  if (!res.ok) throw new Error("❌ No se pudo obtener el perfil");

  return await res.json();  // Devuelve: { id, username, email, is_admin, ... }
};

// -------------------- Solicitar enlace de recuperación --------------------
export const requestPasswordReset = async (email: string) => {
  const res = await fetch(`${API_URL}/auth/forgot-password`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email }),                           // Solo se envía el email
  });

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "No se pudo enviar el correo de recuperación.");
  }

  return await res.json();  // Devuelve un mensaje informativo
};

// -------------------- Restablecer contraseña con token --------------------
export const resetPassword = async (token: string, newPassword: string) => {
  const res = await fetch(`${API_URL}/auth/reset-password`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ token, new_password: newPassword }),
  });

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "No se pudo restablecer la contraseña.");
  }

  return await res.json();  // Devuelve confirmación del cambio
};
