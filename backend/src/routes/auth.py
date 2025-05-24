# backend/src/routes/auth.py

# -------------------- Librerías externas --------------------
from fastapi import APIRouter, Depends, HTTPException, status    # Para definir rutas, dependencias y manejar errores
from sqlalchemy.orm import Session                                # Manejo de sesiones de base de datos con SQLAlchemy

# -------------------- Módulos internos del proyecto --------------------
from src.schemas import UserCreate, UserLogin, UserResponse       # Esquemas para validación y respuesta de usuarios
from src.models import User                                       # Modelo ORM de usuario
from src.database import get_db                                   # Función para obtener sesión de base de datos

# -------------------- Funciones de autenticación --------------------
from src.services.auth_service import (
    hash_password, verify_password, create_access_token,          # Funciones de seguridad
    get_current_user, create_reset_token, verify_reset_token,
    send_recovery_email_simulado                                  # Simulación de envío de correo
)
from src.schemas import ForgotPasswordRequest, ResetPasswordRequest  # Esquemas para recuperación de contraseña

# -------------------- Inicialización del router --------------------
router = APIRouter(prefix="/auth", tags=["Autenticación"])  # Agrupa las rutas relacionadas con autenticación

# -------------------- Ruta: Registro de usuario --------------------
@router.post("/register", response_model=UserResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Registra un nuevo usuario si el correo y username no existen previamente.
    """
    if db.query(User).filter((User.email == user_data.email) | (User.username == user_data.username)).first():
        raise HTTPException(status_code=400, detail="Ya existe un usuario con ese email o username")

    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hash_password(user_data.password)  # Se almacena contraseña hasheada
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# -------------------- Ruta: Login de usuario --------------------
@router.post("/login")
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Verifica credenciales del usuario y retorna un token de acceso JWT.
    """
    user = db.query(User).filter(User.email == credentials.email).first()

    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Correo o contraseña inválidos")

    token = create_access_token(data={"sub": user.id})  # Se genera token con ID de usuario
    return {"access_token": token, "token_type": "bearer"}

# -------------------- Ruta: Obtener perfil del usuario autenticado --------------------
@router.get("/me", response_model=UserResponse)
def get_profile(current_user: User = Depends(get_current_user)):
    """
    Retorna el perfil del usuario autenticado mediante el token.
    """
    return current_user

# -------------------- Ruta: Solicitud de recuperación de contraseña --------------------
@router.post("/forgot-password", summary="Solicita recuperación de contraseña")
def forgot_password(data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """
    Genera un token de recuperación de contraseña y simula el envío por correo.
    """
    user = db.query(User).filter(User.email == data.email).first()

    if not user:
        raise HTTPException(status_code=404, detail="No existe una cuenta con ese email")

    reset_token = create_reset_token(user)
    send_recovery_email_simulado(user.email, reset_token)

    return {
        "message": "Enlace de recuperación generado (simulado)",
        "token": reset_token  # Visible solo para pruebas desde Swagger
    }

# -------------------- Ruta: Restablecimiento de contraseña --------------------
@router.post("/reset-password", summary="Reinicia la contraseña con token")
def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    """
    Valida el token recibido y permite actualizar la contraseña del usuario.
    """
    user = verify_reset_token(data.token, db)

    user.hashed_password = hash_password(data.new_password)  # Almacena la nueva contraseña cifrada
    db.commit()

    return {"message": "Contraseña actualizada correctamente"}
