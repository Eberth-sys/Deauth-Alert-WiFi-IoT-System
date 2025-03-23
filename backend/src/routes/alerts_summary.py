# backend/src/routes/alerts_summary.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text  
from src.database import get_db

router = APIRouter(prefix="/alerts-summary", tags=["Resumen de alertas"])

@router.get("/")
def get_alerts_summary(db: Session = Depends(get_db)):
    try:
        query = text("""
            SELECT canal, COUNT(*) AS total_alertas, MAX(timestamp) AS last_seen
            FROM alerts
            GROUP BY canal
            ORDER BY canal
        """)
        result = db.execute(query).fetchall()

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
                "last_seen": row.last_seen.isoformat() if row.last_seen else None,
                "nodo_iot": canal_to_nodo.get(row.canal, "Desconocido")
            }
            for row in result
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
