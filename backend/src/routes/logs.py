#backend\src\routes\logs.py

import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

# Definir el router para los logs
router = APIRouter(prefix="/logs", tags=["logs"])

# Ruta donde se almacenan los logs en el servidor
LOGS_DIR = "/home/user/GitHub/Deauth-Alert-WiFi-IoT-System/processing-layer/logs"

# - Endpoint para obtener la lista de archivos de logs disponibles
@router.get("/")
def list_logs():
    try:
        files = os.listdir(LOGS_DIR)  # Listar archivos en la carpeta logs
        return {"logs": files}  # Retornar la lista de archivos disponibles
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al listar logs: {e}")

# - Endpoint para ver el contenido de un archivo de log
@router.get("/{log_filename}")
def read_log(log_filename: str):
    log_path = os.path.join(LOGS_DIR, log_filename)

    # Verificar si el archivo existe
    if not os.path.exists(log_path):
        raise HTTPException(status_code=404, detail="Archivo de log no encontrado")

    # Leer y devolver el contenido del archivo
    try:
        with open(log_path, "r", encoding="utf-8") as log_file:
            content = log_file.readlines()
        return {"filename": log_filename, "content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al leer el log: {e}")

# - Endpoint para descargar un archivo de log
@router.get("/download/{log_filename}")
def download_log(log_filename: str):
    log_path = os.path.join(LOGS_DIR, log_filename)

    # Verificar si el archivo existe
    if not os.path.exists(log_path):
        raise HTTPException(status_code=404, detail="Archivo de log no encontrado")

    return FileResponse(log_path, filename=log_filename, media_type="text/plain")
