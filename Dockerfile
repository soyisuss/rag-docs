# ============================================================
# Servidor FastAPI (Google Cloud Run)
# Frontend desacoplado alojado en Cloudflare Pages
# ============================================================
FROM python:3.11-slim

# Instalar uv para instalación rápida y determinista de dependencias
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Variables de entorno para ejecución sin buffer y configuración de red
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080 \
    HOST=0.0.0.0

WORKDIR /app/backend

# Instalar dependencias Python del backend
COPY backend/pyproject.toml backend/uv.lock ./
RUN uv pip install --system --no-cache -r pyproject.toml

# Copiar código backend y estructura de datos
COPY backend/src/ ./src/
COPY backend/data/ ./data/
COPY README.md /app/README.md

# Puerto expuesto para Google Cloud Run
EXPOSE 8080

# Healthcheck nativo consultando el endpoint FastAPI
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')" || exit 1

# Comando de inicio del servidor ASGI (Uvicorn)
ENTRYPOINT ["uvicorn", "src.presentation.main:app", "--host", "0.0.0.0", "--port", "8080"]
