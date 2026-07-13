// frontend/src/types/auth.ts
// Tipo compartido del usuario autenticado (respuesta de /auth/me del backend).
// Se usa en useAuth y AuthContext para evitar `any` duplicado.

export interface User {
  id: number;
  username: string;
  email: string;
  is_admin: boolean;
  created_at: string;
}
