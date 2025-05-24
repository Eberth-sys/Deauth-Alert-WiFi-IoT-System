# backend/src/services/auth_service.py

# -------------------- Librerías estándar de Python --------------------
from datetime import datetime, timedelta                     # Para manejar fechas y tiempos (ej. expiración del token)
import os                                                    # Para acceder a variables del sistema operativo

# -------------------- Librerías externas (instaladas con pip) --------------------
from jose import JWTError, jwt                               # Para crear, codificar y verificar tokens JWT
from passlib.context import CryptContext                     # Para hashear y verificar contraseñas
from fastapi import Depends, HTTPException, status, Request  # Utilidades de FastAPI para manejo de errores y dependencias
from sqlalchemy.orm import Session                           # ORM para interactuar con la base de datos
from dotenv import load_dotenv                               # Para cargar variables desde el archivo .env

# -------------------- Módulos internos del proyecto --------------------
from src.database import get_db                              # Función que retorna la sesión de base de datos
from src.models import User                                  # Modelo de usuario (tabla en la base de datos)
from src.schemas import UserCreate                           # Esquema de entrada para crear usuarios
from src.schemas import ForgotPasswordRequest, ResetPasswordRequest  # Esquemas para recuperación de contraseña

# -------------------- Configuración de variables de entorno --------------------
load_dotenv()

# Claves para firmar y configurar el token JWT
SECRET_KEY = os.getenv("JWT_SECRET_KEY")                                   # Clave secreta del token
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")                            # Algoritmo de cifrado
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "1440")) # Expiración en minutos (por defecto 24h)

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")          # URL del frontend para enlaces

# Validación: si no hay clave secreta, lanzar error crítico
if not SECRET_KEY:
    raise RuntimeError("❌ JWT_SECRET_KEY no está definido en el archivo .env")

# -------------------- Contexto de encriptación para contraseñas --------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# -------------------- Funciones de autenticación --------------------

def hash_password(password: str) -> str:
    """Hashea una contraseña en texto plano"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica si la contraseña ingresada coincide con el hash guardado"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """Crea un token JWT con expiración incluida"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})

    if "sub" in to_encode:
        to_encode["sub"] = str(to_encode["sub"])  # JWT requiere que 'sub' sea string

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_token_from_header(request: Request) -> str:
    """Extrae el token JWT del header Authorization"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token no proporcionado o mal formado")
    return auth_header.split(" ")[1]

def get_current_user(token: str = Depends(get_token_from_header), db: Session = Depends(get_db)) -> User:
    """Decodifica el token y obtiene el usuario autenticado"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
        if user_id is None:
            raise credentials_exception
    except JWTError as e:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise credentials_exception
    return user

# -------------------- Funciones para recuperación de contraseña --------------------

def create_reset_token(user: User) -> str:
    """Genera un token temporal (30 min) para restablecer la contraseña"""
    expire = datetime.utcnow() + timedelta(minutes=30)
    payload = {"sub": str(user.id), "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_reset_token(token: str, db: Session) -> User:
    """Verifica el token recibido para restablecimiento de contraseña"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
        if not user_id:
            raise ValueError("ID inválido en token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user

def send_recovery_email_simulado(email: str, token: str):
    """Simula el envío de un correo con enlace de restablecimiento"""
    reset_link = f"{FRONTEND_URL}/reset-password?token={token}"
    print(f"📧 Simulando envío a {email} con link: {reset_link}")

def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Verifica que el usuario actual tiene permisos de administrador"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso restringido solo para administradores"
        )
    return current_user
