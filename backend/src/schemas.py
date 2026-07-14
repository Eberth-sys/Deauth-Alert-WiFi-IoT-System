# backend/src/schemas.py

# -------------------- Librerías externas --------------------
from pydantic import BaseModel, EmailStr, validator         # Para definir y validar esquemas de datos
from datetime import datetime                               # Para manejar fechas y horas
import re                                                   # Para validación de contraseñas mediante expresiones regulares

# -------------------- Esquemas para Alertas --------------------

# Esquema de entrada para crear una nueva alerta
class AlertCreate(BaseModel):
    nodo_iot: str                    # Nombre del dispositivo que detectó el ataque
    spoofed_bssid: str              # Dirección BSSID falsificada
    target_mac: str                 # Dirección MAC objetivo del ataque
    bssid: str                      # BSSID original del entorno
    canal: int                      # Canal donde se detectó el ataque

# Esquema de salida que extiende AlertCreate con ID y timestamp
class AlertResponse(AlertCreate):
    id: int                         # ID único de la alerta
    timestamp: datetime             # Fecha y hora de detección

    class Config:
        from_attributes = True     # Permite convertir automáticamente desde un modelo SQLAlchemy

# -------------------- Esquema para estado de los nodos ESP32 --------------------

class ESP32StatusResponse(BaseModel):
    device_name: str                # Nombre del nodo ESP32
    mac_address: str                # Dirección MAC del nodo
    status: str                     # Estado actual (ej. 'conectado', 'desconectado')
    last_update: datetime           # Última vez que se actualizó el estado

    class Config:
        from_attributes = True     # Conversión directa desde el modelo SQLAlchemy

# -------------------- Validación y esquemas para Usuarios --------------------

# Lista negra de contraseñas débiles que no se deben permitir
COMMON_PASSWORDS = {
    "123456", "password", "12345678", "qwerty", 
    "admin123", "123456789", "admin", "abc123"
}

# Esquema para registrar un nuevo usuario con validación personalizada de contraseña
class UserCreate(BaseModel):
    username: str                  # Nombre de usuario
    email: EmailStr                # Email válido
    password: str                  # Contraseña con requisitos mínimos

    @validator("password")
    def validate_password(cls, pwd: str) -> str:
        if len(pwd) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres.")
        if not re.search(r"[A-Z]", pwd):
            raise ValueError("Debe contener al menos una letra mayúscula.")
        if not re.search(r"[a-z]", pwd):
            raise ValueError("Debe contener al menos una letra minúscula.")
        if not re.search(r"[0-9]", pwd):
            raise ValueError("Debe contener al menos un número.")
        if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]", pwd):
            raise ValueError("Debe contener al menos un carácter especial.")
        if pwd.lower() in COMMON_PASSWORDS:
            raise ValueError("La contraseña es demasiado común o insegura.")
        return pwd

# Esquema para iniciar sesión
class UserLogin(BaseModel):
    email: EmailStr                # Email del usuario
    password: str                  # Contraseña ingresada

# Esquema de respuesta para mostrar información pública del usuario (sin contraseña)
class UserResponse(BaseModel):
    id: int                        # ID del usuario
    username: str                  # Nombre del usuario
    email: EmailStr                # Email registrado
    is_admin: bool                 # Indica si el usuario es administrador
    created_at: datetime           # Fecha de creación del usuario

    class Config:
        from_attributes = True     # Permite convertir desde SQLAlchemy fácilmente


# Solicitud de recuperación de contraseña (paso 1)
class ForgotPasswordRequest(BaseModel):
    email: EmailStr

# Confirmación de reinicio (paso 2)
class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

    @validator("new_password")
    def validate_new_password(cls, pwd: str) -> str:
        if len(pwd) < 8:
            raise ValueError("La nueva contraseña debe tener al menos 8 caracteres.")
        if not re.search(r"[A-Z]", pwd):
            raise ValueError("Debe contener al menos una letra mayúscula.")
        if not re.search(r"[a-z]", pwd):
            raise ValueError("Debe contener al menos una letra minúscula.")
        if not re.search(r"[0-9]", pwd):
            raise ValueError("Debe contener al menos un número.")
        if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]", pwd):
            raise ValueError("Debe contener al menos un carácter especial.")
        if pwd.lower() in COMMON_PASSWORDS:
            raise ValueError("La nueva contraseña es demasiado común o insegura.")
        return pwd
