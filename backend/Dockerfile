# backend/Dockerfile — imagen del backend FastAPI (D2)
# Contexto de build: ./backend  (usa backend/.dockerignore para NO hornear .env/certs)

FROM python:3.11-slim-bookworm

# No escribir .pyc; salida sin buffer (logs inmediatos); logs dentro del contenedor.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    LOGS_DIR=/app/logs

WORKDIR /app

# 1) Dependencias primero (aprovecha la cache de capas de Docker).
COPY src/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 2) Código de la aplicación.
COPY src ./src

# 3) Usuario NO-root + carpeta de logs escribible por ese usuario.
RUN groupadd -g 1001 app \
 && useradd -u 1001 -g app -m app \
 && mkdir -p /app/logs \
 && chown -R app:app /app
USER app

# Puerto del servidor ASGI.
EXPOSE 8000

# Escucha en 0.0.0.0 para ser accesible desde fuera del contenedor.
# (Sin HEALTHCHECK en D2 a propósito: el /health real con chequeo de BD queda para D3/roadmap.)
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
