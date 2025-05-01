#backend\src\services\auth_service.py
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

# Validación: si no hay clave secreta, lanzar error crítico
if not SECRET_KEY:
    raise RuntimeError("❌ JWT_SECRET_KEY no está definido en el archivo .env")

# -------------------- Contexto de encriptación para contraseñas --------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# -------------------- Funciones de autenticación --------------------

# Hashea una contraseña en texto plano
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# Verifica si la contraseña ingresada coincide con el hash guardado
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Crea un token JWT con expiración incluida
def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})

    # JWT exige que 'sub' (subject) sea tipo string
    if "sub" in to_encode:
        to_encode["sub"] = str(to_encode["sub"])

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Extrae el token JWT del header Authorization
def get_token_from_header(request: Request) -> str:
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token no proporcionado o mal formado")
    return auth_header.split(" ")[1]

# Decodifica el token y obtiene el usuario autenticado
def get_current_user(token: str = Depends(get_token_from_header), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print("📦 Payload JWT:", payload)
        user_id = int(payload.get("sub"))
        print("🔎 user_id extraído:", user_id, type(user_id))
        if user_id is None:
            raise credentials_exception
    except JWTError as e:
        print("❌ Error al decodificar token:", e)
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise credentials_exception
    return user

# -------------------- Funciones para recuperación de contraseña --------------------

# Genera un token temporal (30 min) para restablecer la contraseña
def create_reset_token(user: User) -> str:
    expire = datetime.utcnow() + timedelta(minutes=30)
    payload = {"sub": str(user.id), "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

# Verifica el token recibido para restablecimiento de contraseña
def verify_reset_token(token: str, db: Session) -> User:
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

# Simula el envío de un correo con enlace de restablecimiento (solo demostrativo)
def send_recovery_email_simulado(email: str, token: str):
    reset_link = f"http://localhost:5173/reset-password?token={token}"
    print(f"📧 Simulando envío a {email} con link: {reset_link}")
