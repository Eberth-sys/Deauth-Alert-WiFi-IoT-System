# backend/src/routes/alerts_summary.py

# -------------------- Librerías externas --------------------
from fastapi import APIRouter, Depends, HTTPException             # Para definir rutas, manejar dependencias y errores
from sqlalchemy.orm import Session                                # ORM de SQLAlchemy para sesiones de base de datos
from sqlalchemy import text                                       # Para ejecutar consultas SQL directas

# -------------------- Módulos internos --------------------
from src.database import get_db                                   # Función para obtener una sesión de base de datos

# -------------------- Inicialización del router --------------------
router = APIRouter(prefix="/alerts-summary", tags=["Resumen de alertas"])  # Agrupa las rutas bajo un prefijo y etiqueta

# -------------------- Ruta: Obtener resumen de alertas por canal --------------------
@router.get("/")
def get_alerts_summary(db: Session = Depends(get_db)):
    """
    Consulta un resumen de alertas agrupadas por canal Wi-Fi.
    Retorna el canal, cantidad de alertas, última vez vista,
    el nodo que reportó y detalles de la última alerta (BSSID y MAC objetivo).
    """
    try:
        # Consulta SQL avanzada para obtener el resumen de alertas por canal
        query = text("""
            SELECT a.canal,
                   COUNT(*) AS total_alertas,
                   MAX(a.timestamp) AS last_seen,
                   last_event.spoofed_bssid,
                   last_event.target_mac
            FROM alerts a
            JOIN LATERAL (
                SELECT spoofed_bssid, target_mac
                FROM alerts
                WHERE canal = a.canal
                ORDER BY timestamp DESC
                LIMIT 1
            ) AS last_event ON true
            GROUP BY a.canal, last_event.spoofed_bssid, last_event.target_mac
            ORDER BY a.canal;
        """)
        result = db.execute(query).fetchall()

        # Mapeo de canales a nombres de nodos ESP32
        canal_to_nodo = {
            1: "ESP32_1_CH_01",
            6: "ESP32_2_CH_06",
            11: "ESP32_3_CH_11",
        }
        for ch in [2, 3, 4, 5, 7, 8, 9, 10, 12, 13, 14]:
            canal_to_nodo[ch] = "ESP32_4_SCANN"

        # Preparar y retornar la respuesta
        return [
            {
                "canal": row.canal,
                "count": row.total_alertas,
                "last_seen": row.last_seen.isoformat() if row.last_seen else None,
                "nodo_iot": canal_to_nodo.get(row.canal, "Desconocido"),
                "spoofed_bssid": row.spoofed_bssid,
                "target_mac": row.target_mac
            }
            for row in result
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))  # Manejo de errores generales
