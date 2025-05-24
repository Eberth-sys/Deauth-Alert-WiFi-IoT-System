#backend\src\routes\logs.py

# -------------------- Importaciones --------------------
import os                                           # Para manejar rutas y archivos del sistema
from fastapi import APIRouter, HTTPException        # Para definir rutas y manejar excepciones HTTP
from fastapi.responses import FileResponse          # Para retornar archivos como respuesta
from dotenv import load_dotenv                      # Para cargar variables de entorno desde .env

# -------------------- Cargar configuración desde .env --------------------
load_dotenv()  # Carga las variables definidas en el archivo .env

# -------------------- Definir router --------------------
router = APIRouter(prefix="/logs", tags=["logs"])  # Prefijo y etiqueta para las rutas de logs

# -------------------- Ruta donde se almacenan los logs --------------------
LOGS_DIR = os.getenv("LOGS_DIR", "processing-layer/logs")  # Ruta desde .env, o por defecto

# -------------------- Endpoint: Listar archivos de logs --------------------
@router.get("/")
def list_logs():
    """
    Retorna una lista de nombres de archivos de log disponibles.
    """
    try:
        files = os.listdir(LOGS_DIR)
        return {"logs": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al listar logs: {e}")

# -------------------- Endpoint: Leer contenido de un log --------------------
@router.get("/{log_filename}")
def read_log(log_filename: str):
    """
    Retorna el contenido línea por línea de un archivo de log específico.
    """
    log_path = os.path.join(LOGS_DIR, log_filename)

    if not os.path.exists(log_path):
        raise HTTPException(status_code=404, detail="Archivo de log no encontrado")

    try:
        with open(log_path, "r", encoding="utf-8") as log_file:
            content = log_file.readlines()
        return {"filename": log_filename, "content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al leer el log: {e}")

# -------------------- Endpoint: Descargar archivo de log --------------------
@router.get("/download/{log_filename}")
def download_log(log_filename: str):
    """
    Permite descargar un archivo de log como texto plano.
    """
    log_path = os.path.join(LOGS_DIR, log_filename)

    if not os.path.exists(log_path):
        raise HTTPException(status_code=404, detail="Archivo de log no encontrado")

    return FileResponse(log_path, filename=log_filename, media_type="text/plain")
