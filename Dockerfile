# ============================================================
# ETAPA 1: Construcción del Frontend (React + TypeScript con Vite)
# ============================================================
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

# Copiar manifiesto de dependencias para optimizar caché de capas Docker
COPY frontend/package.json frontend/package-lock.json* ./

RUN npm install

# Copiar código fuente del frontend y compilar bundle de producción
COPY frontend/ ./
RUN npm run build


# ============================================================
# ETAPA 2: Imagen Final del Servidor (FastAPI + Clean Architecture)
# ============================================================
FROM python:3.11-slim

# Instalar uv para una instalación reproducible y ultra-rápida de dependencias
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

# Copiar bundle estático del frontend compilado en la Etapa 1
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

# Puerto expuesto para Google Cloud Run y ejecución local
EXPOSE 8080

# Healthcheck nativo consultando el endpoint FastAPI
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')" || exit 1

# Comando de inicio del servidor ASGI (Uvicorn)
ENTRYPOINT ["uvicorn", "src.presentation.main:app", "--host", "0.0.0.0", "--port", "8080"]
