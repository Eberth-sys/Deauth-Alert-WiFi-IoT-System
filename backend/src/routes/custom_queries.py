#backend\src\routes\custom_queries.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
from src.database import get_db

router = APIRouter(prefix="/custom-queries", tags=["Consultas Personalizadas"])

@router.get("/ultimas-alertas")
def ultimas_alertas(db: Session = Depends(get_db)):
    query = text("SELECT * FROM alerts ORDER BY timestamp DESC LIMIT 10")
    result = db.execute(query).fetchall()
    return [dict(row._mapping) for row in result]

@router.get("/total-alertas")
def total_alertas(db: Session = Depends(get_db)):
    query = text("SELECT COUNT(*) FROM alerts")
    result = db.execute(query).scalar()
    return {"total_alertas": result}

@router.get("/alertas-por-nodo")
def alertas_por_nodo(db: Session = Depends(get_db)):
    query = text("SELECT nodo_iot, COUNT(*) AS total_alertas FROM alerts GROUP BY nodo_iot ORDER BY total_alertas DESC")
    result = db.execute(query).fetchall()
    return [dict(row._mapping) for row in result]

@router.get("/canales-mas-afectados")
def canales_mas_afectados(db: Session = Depends(get_db)):
    query = text("SELECT canal, COUNT(*) AS total_alertas FROM alerts GROUP BY canal ORDER BY total_alertas DESC")
    result = db.execute(query).fetchall()
    return [dict(row._mapping) for row in result]

@router.get("/alertas-de-hoy")
def alertas_de_hoy(db: Session = Depends(get_db)):
    query = text("""
        SELECT * FROM alerts
        WHERE timestamp::date = CURRENT_DATE
        ORDER BY timestamp ASC
    """)
    result = db.execute(query).fetchall()
    return [dict(row._mapping) for row in result]

@router.get("/alertas-por-fecha")
def alertas_por_fecha(start: str, end: str, db: Session = Depends(get_db)):
    try:
        if 'T' not in start:
            start += " 00:00:00"
        if 'T' not in end:
            end += " 23:59:59"

        start_dt = datetime.fromisoformat(start)
        end_dt = datetime.fromisoformat(end)

        query = text("""
            SELECT * FROM alerts
            WHERE timestamp BETWEEN :start AND :end
            ORDER BY timestamp ASC
        """)
        result = db.execute(query, {"start": start_dt, "end": end_dt}).fetchall()
        return [dict(row._mapping) for row in result]
    except Exception as e:
        return {"error": f"❌ Consulta inválida: {str(e)}"}
