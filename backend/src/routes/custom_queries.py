# backend/src/routes/custom_queries.py

# -------------------- Importaciones --------------------
from fastapi import APIRouter, Depends                   # FastAPI y dependencia para base de datos
from sqlalchemy.orm import Session                       # Sesión de SQLAlchemy
from sqlalchemy import text                              # Permite ejecutar consultas SQL en crudo
from datetime import datetime                            # Manejo de fechas y horas
from src.database import get_db                          # Función para obtener la sesión de la base de datos
from src.services.auth_service import get_current_user   # Autenticación JWT de usuario (T2, SEC-02)

# -------------------- Definir router --------------------
router = APIRouter(prefix="/custom-queries", tags=["Consultas Personalizadas"])  # Ruta base y etiqueta para Swagger

# -------------------- Consultas personalizadas --------------------

# Obtener las 10 alertas más recientes
@router.get("/ultimas-alertas", dependencies=[Depends(get_current_user)])
def ultimas_alertas(db: Session = Depends(get_db)):
    query = text("SELECT * FROM alerts ORDER BY timestamp DESC LIMIT 10")  # Consulta SQL directa
    result = db.execute(query).fetchall()  # Ejecutar consulta
    return [dict(row._mapping) for row in result]  # Convertir a lista de diccionarios

# Contar el total de alertas en la base de datos
@router.get("/total-alertas", dependencies=[Depends(get_current_user)])
def total_alertas(db: Session = Depends(get_db)):
    query = text("SELECT COUNT(*) FROM alerts")
    result = db.execute(query).scalar()  # Obtener valor único
    return {"total_alertas": result}

# Agrupar alertas por nodo IoT
@router.get("/alertas-por-nodo", dependencies=[Depends(get_current_user)])
def alertas_por_nodo(db: Session = Depends(get_db)):
    query = text("""
        SELECT nodo_iot, COUNT(*) AS total_alertas 
        FROM alerts 
        GROUP BY nodo_iot 
        ORDER BY total_alertas DESC
    """)
    result = db.execute(query).fetchall()
    return [dict(row._mapping) for row in result]

# Mostrar los canales Wi-Fi más afectados
@router.get("/canales-mas-afectados", dependencies=[Depends(get_current_user)])
def canales_mas_afectados(db: Session = Depends(get_db)):
    query = text("""
        SELECT canal, COUNT(*) AS total_alertas 
        FROM alerts 
        GROUP BY canal 
        ORDER BY total_alertas DESC
    """)
    result = db.execute(query).fetchall()
    return [dict(row._mapping) for row in result]

# Consultar alertas generadas en el día actual
@router.get("/alertas-de-hoy", dependencies=[Depends(get_current_user)])
def alertas_de_hoy(db: Session = Depends(get_db)):
    query = text("""
        SELECT * FROM alerts
        WHERE timestamp::date = CURRENT_DATE
        ORDER BY timestamp ASC
    """)
    result = db.execute(query).fetchall()
    return [dict(row._mapping) for row in result]

# Consultar alertas entre dos fechas específicas
@router.get("/alertas-por-fecha", dependencies=[Depends(get_current_user)])
def alertas_por_fecha(start: str, end: str, db: Session = Depends(get_db)):
    try:
        # Si no se especifica hora, se asume todo el día
        if 'T' not in start:
            start += " 00:00:00"
        if 'T' not in end:
            end += " 23:59:59"

        # Convertir strings a objetos datetime
        start_dt = datetime.fromisoformat(start)
        end_dt = datetime.fromisoformat(end)

        # Consulta filtrada por intervalo de fechas
        query = text("""
            SELECT * FROM alerts
            WHERE timestamp BETWEEN :start AND :end
            ORDER BY timestamp ASC
        """)
        result = db.execute(query, {"start": start_dt, "end": end_dt}).fetchall()
        return [dict(row._mapping) for row in result]
    except Exception as e:
        return {"error": f"❌ Consulta inválida: {str(e)}"}
