# backend/src/services/service_auth.py

# -------------------- Librerías estándar de Python --------------------
import os                                                    # Para leer variables de entorno
import secrets                                               # Comparación en tiempo constante (resistente a timing attacks)

# -------------------- Librerías externas (instaladas con pip) --------------------
from fastapi import Header, HTTPException, status            # Header para leer 'X-API-Key' y utilidades de error
from dotenv import load_dotenv                               # Para cargar variables desde el archivo .env

# -------------------- Configuración de variables de entorno --------------------
load_dotenv()

# Secreto compartido con la processing-layer (Raspberry Pi). Ver DEC-0005.
SERVICE_API_KEY = os.getenv("SERVICE_API_KEY")

# Valor placeholder del .env.example: nunca debe aceptarse como clave real.
PLACEHOLDER_SERVICE_API_KEY = "your_strong_service_api_key"
# Longitud mínima exigida. `secrets.token_urlsafe(32)` genera ~43 caracteres.
MIN_SERVICE_API_KEY_LENGTH = 32


def _service_key_problem(raw_key: str | None) -> str | None:
    """
    Valida la clave de servicio CONFIGURADA en el servidor (no la del cliente).

    Devuelve None si es válida, o un texto describiendo el problema (para log
    server-side; nunca se expone al cliente). Rechaza:
      - clave ausente o vacía;
      - espacios accidentales al inicio/final (error típico al pegar en el .env);
      - el placeholder del .env.example;
      - claves más cortas que MIN_SERVICE_API_KEY_LENGTH.
    """
    if not raw_key:
        return "SERVICE_API_KEY no está definida"
    if raw_key != raw_key.strip():
        return "SERVICE_API_KEY tiene espacios al inicio o al final (revisá el .env)"
    if raw_key == PLACEHOLDER_SERVICE_API_KEY:
        return "SERVICE_API_KEY conserva el valor placeholder del .env.example"
    if len(raw_key) < MIN_SERVICE_API_KEY_LENGTH:
        return f"SERVICE_API_KEY es demasiado corta (mínimo {MIN_SERVICE_API_KEY_LENGTH} caracteres)"
    return None


# Aviso temprano en el arranque si la clave está mal configurada (no se expone al cliente).
_startup_problem = _service_key_problem(SERVICE_API_KEY)
if _startup_problem:
    print(f"[CONFIG] ⚠️ {_startup_problem} — POST /esp32-nodes/update rechazará "
          "todas las peticiones con 500 (fail-safe) hasta corregir la clave.")


# -------------------- Dependencia: Autenticación máquina-a-máquina --------------------
def verify_service_key(x_api_key: str = Header(default=None, alias="X-API-Key")) -> None:
    """
    Autenticación máquina-a-máquina (DEC-0005).

    Valida el header 'X-API-Key' contra `SERVICE_API_KEY` (definida en .env)
    usando `secrets.compare_digest` — comparación en tiempo constante,
    resistente a *timing attacks* — NUNCA `==`.

    Se aplica a los endpoints consumidos por la processing-layer (Raspberry Pi),
    que es un cliente de máquina y no dispone de una sesión de usuario JWT.

    No retorna valor: se usa como dependencia de efecto (levanta excepción si falla).
    """
    # Fail-safe de configuración: si la clave del servidor falta, es el placeholder,
    # tiene espacios o es demasiado corta, el endpoint NO debe aceptar ninguna
    # petición (responde 500, nunca queda accidentalmente abierto).
    if _service_key_problem(SERVICE_API_KEY):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Autenticación de servicio no configurada correctamente en el servidor",
        )

    # Se comparan como bytes para evitar un TypeError si el header trae
    # caracteres no-ASCII (evita un vector de DoS por 500).
    provided = (x_api_key or "").encode("utf-8")
    expected = SERVICE_API_KEY.encode("utf-8")

    if not x_api_key or not secrets.compare_digest(provided, expected):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Clave de servicio inválida o ausente",
        )
