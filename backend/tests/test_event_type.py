# backend/tests/test_event_type.py
# Tests mínimos F1b (DEC-0003): event_type en schema y modelo.
# Sin hardware ni base de datos real (create_engine de SQLAlchemy es lazy: no conecta al importar).
import pytest
from pydantic import ValidationError

from src.schemas import AlertCreate, AlertResponse
from src.models import Alert

BASE = dict(
    nodo_iot="ESP32_1_CH_01",
    spoofed_bssid="00:00:00:00:00:00",
    target_mac="00:00:00:00:00:00",
    bssid="00:00:00:00:00:00",
    canal=1,
)


def test_schema_default_deauth():
    """1) Alerta legacy sin event_type -> default 'deauth'."""
    assert AlertCreate(**BASE).event_type == "deauth"


def test_schema_disassoc_ok():
    """2) event_type='disassoc' -> aceptado."""
    assert AlertCreate(**BASE, event_type="disassoc").event_type == "disassoc"


def test_schema_invalid_rejected():
    """3) event_type inválido -> rechazado (ValidationError)."""
    with pytest.raises(ValidationError):
        AlertCreate(**BASE, event_type="foo")


def test_model_has_event_type_column():
    """El modelo ORM tiene event_type NOT NULL con default 'deauth'."""
    col = Alert.__table__.c.event_type
    assert col is not None
    assert col.nullable is False
    assert str(col.type).startswith("VARCHAR")
    assert "deauth" in str(col.server_default.arg)


def test_response_exposes_event_type():
    """AlertResponse (salida de la API) hereda event_type -> el GET lo expone."""
    assert "event_type" in AlertResponse.model_fields
