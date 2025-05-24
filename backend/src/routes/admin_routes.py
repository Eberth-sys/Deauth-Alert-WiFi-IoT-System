# backend/src/routes/admin_routes.py

# -------------------- Importaciones externas --------------------
from fastapi import APIRouter, Depends                      # Para definir rutas y usar dependencias
from sqlalchemy.orm import Session                         # Para manejar sesiones de base de datos

# -------------------- Importaciones internas --------------------
from src.models import User                                # Modelo ORM de usuario
from src.database import get_db                            # Función para obtener sesión de la base de datos
from src.services.auth_service import get_current_admin_user  # Verifica si el usuario autenticado es admin

# -------------------- Inicialización del router --------------------
router = APIRouter(prefix="/admin", tags=["Administrador"])  # Prefijo y etiqueta para las rutas de administrador

# -------------------- Ruta: Vista de logs solo para administradores --------------------
@router.get("/logs", summary="Vista de logs (solo admin)")
def get_logs_page(current_admin: User = Depends(get_current_admin_user), db: Session = Depends(get_db)):
    """
    Proporciona acceso a la vista de logs solo si el usuario autenticado es un administrador.
    """
    return {
        "page": "logs",
        "message": f"Bienvenido admin {current_admin.username}, accediendo a LogsPage.",
        "can_view": True
    }

# -------------------- Ruta: Vista de reportes solo para administradores --------------------
@router.get("/reports", summary="Vista de reportes (solo admin)")
def get_reports_page(current_admin: User = Depends(get_current_admin_user), db: Session = Depends(get_db)):
    """
    Proporciona acceso a la vista de reportes solo si el usuario autenticado es un administrador.
    """
    return {
        "page": "reports",
        "message": f"Bienvenido admin {current_admin.username}, accediendo a ReportsPage.",
        "can_view": True
    }
