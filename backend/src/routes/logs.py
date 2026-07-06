#backend\src\routes\logs.py

# -------------------- Importaciones --------------------
import os                                           # Para manejar rutas y archivos del sistema
from fastapi import APIRouter, HTTPException, Depends  # Rutas, errores y dependencias
from fastapi.responses import FileResponse          # Para retornar archivos como respuesta
from dotenv import load_dotenv                      # Para cargar variables de entorno desde .env

from src.services.auth_service import get_current_admin_user  # Acceso solo para administradores (T4/SEC-03)

# -------------------- Cargar configuración desde .env --------------------
load_dotenv()  # Carga las variables definidas en el archivo .env

# -------------------- Definir router --------------------
router = APIRouter(prefix="/logs", tags=["logs"])  # Prefijo y etiqueta para las rutas de logs

# -------------------- Ruta donde se almacenan los logs --------------------
LOGS_DIR = os.getenv("LOGS_DIR", "processing-layer/logs")  # Ruta desde .env, o por defecto

# -------------------- Helper: ruta segura dentro de LOGS_DIR (anti path traversal) --------------------
def _safe_log_path(log_filename: str) -> str:
    """
    Devuelve la ruta absoluta segura de un log dentro de LOGS_DIR, o levanta
    HTTPException 400 si el nombre intenta escapar del directorio o no es un .log.

    Defensa contra path traversal (SEC-03): descarta componentes de directorio
    con basename, exige extensión .log (allowlist) y confina el resultado a
    LOGS_DIR con realpath + commonpath. Rechaza ../, backslash, rutas absolutas,
    variantes URL-encoded (ya decodificadas) y nombres no-.log.
    """
    # Rechazo PORTABLE de separadores de ruta ANTES de normalizar: os.path.basename
    # trata '\' distinto en Windows vs Linux, así que no dependemos de él para
    # bloquear traversal. Cualquier '/' o '\' en el nombre -> inválido (defensa portable).
    if "/" in log_filename or "\\" in log_filename:
        raise HTTPException(status_code=400, detail="Nombre de archivo de log inválido")

    safe_name = os.path.basename(log_filename)                 # defensa extra (aquí ya no debería cambiar el nombre)
    if safe_name != log_filename or not safe_name.endswith(".log"):
        raise HTTPException(status_code=400, detail="Nombre de archivo de log inválido")

    base = os.path.realpath(LOGS_DIR)
    candidate = os.path.realpath(os.path.join(base, safe_name))
    try:
        if os.path.commonpath([base, candidate]) != base:      # candidate DEBE quedar dentro de base
            raise HTTPException(status_code=400, detail="Nombre de archivo de log inválido")
    except ValueError:                                         # rutas incomparables (p.ej. otro drive)
        raise HTTPException(status_code=400, detail="Nombre de archivo de log inválido")
    return candidate

# -------------------- Endpoint: Listar archivos de logs (solo admin) --------------------
@router.get("/", dependencies=[Depends(get_current_admin_user)])
def list_logs():
    """
    Retorna la lista de archivos .log disponibles. Requiere rol de administrador.
    """
    try:
        files = os.listdir(LOGS_DIR)
        return {"logs": [f for f in files if f.endswith(".log")]}  # solo .log (coherente con el allowlist)
    except Exception as e:
        print(f"[LOGS] Error al listar logs: {e}")             # detalle solo en el servidor (no al cliente)
        raise HTTPException(status_code=500, detail="No se pudieron listar los logs")

# -------------------- Endpoint: Leer contenido de un log (solo admin) --------------------
@router.get("/{log_filename}", dependencies=[Depends(get_current_admin_user)])
def read_log(log_filename: str):
    """
    Retorna el contenido línea por línea de un archivo de log. Requiere rol admin.
    """
    log_path = _safe_log_path(log_filename)

    if not os.path.exists(log_path):
        raise HTTPException(status_code=404, detail="Archivo de log no encontrado")

    try:
        with open(log_path, "r", encoding="utf-8") as log_file:
            content = log_file.readlines()
        return {"filename": os.path.basename(log_path), "content": content}
    except Exception as e:
        print(f"[LOGS] Error al leer el log: {e}")             # detalle solo en el servidor (no al cliente)
        raise HTTPException(status_code=500, detail="No se pudo leer el archivo de log")

# -------------------- Endpoint: Descargar archivo de log (solo admin) --------------------
@router.get("/download/{log_filename}", dependencies=[Depends(get_current_admin_user)])
def download_log(log_filename: str):
    """
    Permite descargar un archivo de log como texto plano. Requiere rol admin.
    """
    log_path = _safe_log_path(log_filename)

    if not os.path.exists(log_path):
        raise HTTPException(status_code=404, detail="Archivo de log no encontrado")

    return FileResponse(log_path, filename=os.path.basename(log_path), media_type="text/plain")
