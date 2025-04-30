#backend\src\services\auth_service.py

# Librerías estándar de Python
from datetime import datetime, timedelta                     # Para manejar fechas y tiempos (ej. expiración del token)
import os                                                    # Permite acceder a las variables del sistema operativo

# Librerías externas (instaladas con pip)
from jose import JWTError, jwt                               # Para crear, decodificar y verificar tokens JWT
from passlib.context import CryptContext                     # Para hashear y verificar contraseñas de forma segura
from fastapi import Depends, HTTPException, status, Request  # Utilidades de FastAPI para dependencias y manejo de errores
from sqlalchemy.orm import Session                           # Para trabajar con la base de datos usando SQLAlchemy
from dotenv import load_dotenv                               # Carga variables del entorno desde un archivo .env

# Importaciones locales del proyecto
from src.database import get_db                              # Función que retorna la conexión (sesión) a la base de datos
from src.models import User                                  # Modelo de usuario (estructura de la tabla en la base de datos)
from src.schemas import UserCreate                           # Esquema para validar los datos al crear un usuario

# Cargar variables de entorno
load_dotenv()

# Claves de configuración del token 
SECRET_KEY = os.getenv("JWT_SECRET_KEY")                                   # Clave secreta usada para firmar el token JWT
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")                            # Algoritmo de encriptación del token (por defecto "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "1440")) # Tiempo de expiración del token en minutos (por defecto 1440 = 24 horas)

# Validación: si no hay clave secreta, lanzar error
if not SECRET_KEY:
    raise RuntimeError("❌ JWT_SECRET_KEY no está definido en el archivo .env")

# Contexto de hash para contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Hashea una contraseña en texto plano
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


# Verifica si una contraseña coincide con su hash
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})

    # JWT exige que el 'sub' sea string
    if "sub" in to_encode:
        to_encode["sub"] = str(to_encode["sub"])

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Extrae el token del header Authorization
def get_token_from_header(request: Request) -> str:
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token no proporcionado o mal formado")
    return auth_header.split(" ")[1]

# Extrae el usuario autenticado desde el token
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
