# backend/src/routes/alerts_summary.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text  # ejecutar SQL sin errores
from src.database import get_db

router = APIRouter(
    prefix="/alerts-summary",
    tags=["Resumen de alertas"]
)

@router.get("/")
def get_alerts_summary(db: Session = Depends(get_db)):
    query = """
        SELECT canal, COUNT(*) AS total_alertas
        FROM alerts
        GROUP BY canal
        ORDER BY canal
    """
    result = db.execute(text(query)).fetchall()

    # Mapeo de canal a nodo
    canal_to_nodo = {
        1: "ESP32_1_CH_01",
        6: "ESP32_2_CH_06",
        11: "ESP32_3_CH_11",
    }
    for ch in [2, 3, 4, 5, 7, 8, 9, 10, 12, 13, 14]:
        canal_to_nodo[ch] = "ESP32_4_SCANN"

    return [
        {
            "canal": row.canal,
            "count": row.total_alertas,
            "nodo_iot": canal_to_nodo.get(row.canal, "Desconocido")
        }
        for row in result
    ]
