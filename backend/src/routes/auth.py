#backend\src\routes\auth.py

# -------------------- Librerías externas --------------------
from fastapi import APIRouter, Depends, HTTPException, status  # Herramientas de FastAPI para definir rutas, dependencias y manejo de errores
from sqlalchemy.orm import Session                              # Sesión de base de datos con SQLAlchemy


# -------------------- Módulos internos --------------------
from src.schemas import UserCreate, UserLogin, UserResponse     # Esquemas de entrada y salida para usuarios
from src.models import User                                     # Modelo ORM del usuario (tabla en la base de datos)
from src.database import get_db                                 # Función que retorna la sesión activa de la base de datos
from src.schemas import UserLogin                               # Importa el esquema Pydantic para validar los datos de inicio de sesión
from src.services.auth_service import (                         # Funciones del servicio de autenticación
    hash_password, verify_password,                             # Para hashear y verificar contraseñas
    create_access_token, get_current_user                       # Para generar tokens y obtener el usuario autenticado
)

# -------------------- Inicialización del router --------------------
router = APIRouter(prefix="/auth", tags=["Autenticación"])      # Sección de rutas bajo el prefijo /auth y con la etiqueta "Autenticación"


# Registro de nuevo usuario
@router.post("/register", response_model=UserResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    # Verifica si ya existe un usuario con ese email o username
    if db.query(User).filter((User.email == user_data.email) | (User.username == user_data.username)).first():
        raise HTTPException(status_code=400, detail="Ya existe un usuario con ese email o username")

    # Crear usuario nuevo
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hash_password(user_data.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

# Login y obtención de token
@router.post("/login")
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Correo o contraseña inválidos")

    # Crear token JWT
    token = create_access_token(data={"sub": user.id})
    return {"access_token": token, "token_type": "bearer"}

# Obtener perfil de usuario autenticado
@router.get("/me", response_model=UserResponse)
def get_profile(current_user: User = Depends(get_current_user)):
    return current_user
