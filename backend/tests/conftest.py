# backend/tests/conftest.py
# Variables de entorno dummy para que src.database arme una URL parseable
# SIN conectar a PostgreSQL (create_engine es lazy). Los tests F1b solo usan
# metadata del modelo y validación de esquemas, no la base real.
import os

os.environ.setdefault("PG_HOST", "localhost")
os.environ.setdefault("PG_PORT", "5432")
os.environ.setdefault("PG_DB", "test")
os.environ.setdefault("PG_USER", "test")
os.environ.setdefault("PG_PASSWORD", "test")
