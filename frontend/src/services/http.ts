//frontend\src\services\http.ts

// -------------------- Clave del token JWT en localStorage --------------------
// Fuente única de la clave para el código que consume la API autenticada (T2).
// Nota: useAuth.ts mantiene su propia copia con el MISMO valor; unificarla es un
// follow-up trivial que queda fuera del alcance de T2.
export const TOKEN_KEY = "auth_token";

// -------------------- Obtener el token JWT actual --------------------
export const getToken = (): string | null => localStorage.getItem(TOKEN_KEY);

// -------------------- Header de autorización para fetch --------------------
// Devuelve { Authorization: "Bearer <token>" } si hay sesión, o {} si no hay token.
// De este modo el header solo se envía cuando existe token (comportamiento T2).
export const authHeader = (): Record<string, string> => {
  const token = getToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
};
