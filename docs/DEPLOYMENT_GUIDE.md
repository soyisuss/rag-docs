# 🚀 Guía Definitiva de Despliegue - Yael Bot

> **Plataforma:** Yael Bot - Minimalist Corporate Document Intelligence Platform  
> **Arquitectura:** FastAPI (Clean Architecture) + React 18 / TypeScript (Vite + Tailwind CSS)  
> **Contenedor:** Docker Multi-stage (Node.js 20 Alpine + Python 3.11 Slim con `uv`)  
> **Entorno Cloud Primario:** Google Cloud Run (Serverless)  
> **Entorno Local / On-Premise:** Docker Engine / Docker Compose  

---

## 📋 Tabla de Contenidos

1. [Estrategia y Arquitectura de Despliegue](#1-estrategia-y-arquitectura-de-despliegue)
2. [Prerrequisitos de Infraestructura y Cuentas](#2-prerrequisitos-de-infraestructura-y-cuentas)
3. [Variables de Entorno y Manejo de Secretos](#3-variables-de-entorno-y-manejo-de-secretos)
4. [El Proceso de Construcción Multi-Stage (`Dockerfile`)](#4-el-proceso-de-construcción-multi-stage-dockerfile)
5. [Despliegue en Google Cloud Run (Paso a Paso)](#5-despliegue-en-google-cloud-run-paso-a-paso)
6. [Despliegue Local / Servidor On-Premise con Docker](#6-despliegue-local--servidor-on-premise-con-docker)
7. [Monitoreo, Diagnóstico y Health Checks](#7-monitoreo-diagnóstico-y-health-checks)
8. [Resolución de Problemas Frecuentes (Troubleshooting)](#8-resolución-de-problemas-frecuentes-troubleshooting)
9. [Lista de Verificación Pre-Despliegue (Checklist)](#9-lista-de-verificación-pre-despliegue-checklist)

---

## 🏛️ 1. Estrategia y Arquitectura de Despliegue

Yael Bot está concebido para desplegarse como un **artefacto único unificado y reproducible**. En lugar de requerir despliegues separados e independientes para frontend y backend con complejas políticas de CORS o dominios cruzados, el sistema compila la aplicación web estática (React SPA) y la sirve de manera nativa mediante FastAPI desde el mismo proceso ASGI (Uvicorn).

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        DOCKER CONTAINER (8080)                         │
│                                                                        │
│   FastAPI ASGI Server (Uvicorn)                                       │
│   ├── /health, /api/health       -> Health Check & Status              │
│   ├── /docs, /openapi.json       -> Swagger UI interactivo             │
│   ├── /api/chat                  -> Inferencia RAG + Guardrails        │
│   ├── /api/documents/*           -> Gestión documental y vectores      │
│   └── /* (Staticfiles / SPA)     -> Sirve frontend/dist (React 18)     │
└───────────────────┬────────────────────────────────┬───────────────────┘
                    │                                │
                    ▼                                ▼
       ┌────────────────────────┐       ┌────────────────────────┐
       │     Qdrant Cloud       │       │    Google Gemini API   │
       │    (Base Vectorial)    │       │  (Embeddings & Flash)  │
       └────────────────────────┘       └────────────────────────┘
```

### Ventajas de esta arquitectura para producción:
- **Zero CORS Issues:** Al servirse desde el mismo origen (`host:port`), se eliminan por completo los bloqueos por cabeceras CORS en navegadores.
- **Portabilidad Absoluta:** La misma imagen de contenedor se ejecuta idénticamente en la estación de un desarrollador, en un servidor privado Linux, o en Google Cloud Run.
- **Ahorro de Costos Serverless:** Permite escalar a **0 instancias** en Cloud Run cuando no hay tráfico activo, reduciendo a cero el costo computacional ocioso.

---

## 🔑 2. Prerrequisitos de Infraestructura y Cuentas

Antes de ejecutar un despliegue, verifica que cuentes con los siguientes servicios y credenciales activos:

### A. Google Cloud Platform (GCP)
1. **Proyecto GCP Activo:** Por ejemplo `yisussapps` (ID numérico de proyecto asociado).
2. **APIs Habilitadas en el Proyecto:**
   ```bash
   gcloud services enable \
       run.googleapis.com \
       cloudbuild.googleapis.com \
       artifactregistry.googleapis.com
   ```
3. **Roles IAM Requeridos:**
   - Si despliegas con tu cuenta personal o de servicio, asegúrate de contar con los roles:
     - `roles/run.admin` (Administrador de Cloud Run)
     - `roles/cloudbuild.builds.editor` (Editor de Cloud Build)
     - `roles/iam.serviceAccountUser` (Usuario de cuenta de servicio de Compute Engine)
4. **Google Cloud SDK (`gcloud` CLI):** Instalado y autenticado en tu terminal:
   ```bash
   gcloud auth login
   gcloud config set project [TU_PROJECT_ID]
   ```

### B. Google Gemini API (Google AI Studio)
- Una API Key válida generada desde [Google AI Studio](https://aistudio.google.com/).
- Cuota suficiente para los modelos:
  - Generación de respuestas: `gemini-3.8-flash`
  - Generación de vectores: `gemini-embedding-001` (768 dimensiones)

### C. Qdrant Cloud (Cluster Vectorial Remoto)
- Un cluster activo en [Qdrant Cloud](https://cloud.qdrant.io/).
- **URL del Cluster:** Endpoint HTTPS con terminación `.qdrant.io` (ej. `https://xxx.us-central1-0.gcp.cloud.qdrant.io`).
- **API Key (JWT):** Token con permisos de lectura y escritura sobre la colección.
- **Colección:** Nombre de la colección (`documents`). Los vectores deben estar configurados en **768 dimensiones** con métrica **Coseno**.

---

## 🔐 3. Variables de Entorno y Manejo de Secretos

El comportamiento del contenedor se gobierna estrictamente a través de variables de entorno. 

### Matriz de Configuración:

| Variable | Tipo | Valor por Defecto | Crítica | Descripción |
| :--- | :--- | :--- | :---: | :--- |
| `PORT` | Entero | `8080` | Sí | Puerto donde escucha Uvicorn. Cloud Run lo inyecta automáticamente. |
| `HOST` | String | `0.0.0.0` | Sí | Dirección de escucha en el contenedor. |
| `GEMINI_API_KEY` | String | Ninguno | **Sí** | Credencial de Google AI Studio para embeddings y síntesis. |
| `QDRANT_URL` | String | Ninguno | **Sí** | URL HTTPS completa del cluster Qdrant Cloud. |
| `QDRANT_API_KEY` | String | Ninguno | **Sí** | Token API de autenticación con Qdrant. |
| `QDRANT_COLLECTION` | String | `documents` | No | Nombre de la colección vectorial destino. |
| `SIMILARITY_THRESHOLD`| Float | `0.70` | No | Umbral de similitud coseno para el guardrail anti-alucinaciones. |
| `TOP_K_RESULTS` | Entero | `3` | No | Número de fragmentos más relevantes recuperados. |
| `GEMINI_MODEL` | String | `gemini-3.8-flash` | No | Identificador del modelo generativo. |
| `GEMINI_EMBEDDING_MODEL`| String | `gemini-embedding-001` | No | Identificador del modelo de embeddings. |
| `VECTOR_DIMENSION` | Entero | `768` | No | Dimensionalidad vectorial de los embeddings. |
| `DATA_DIR` | Ruta | `/app/backend/data/raw` | No | Directorio donde se guardan físicamente los PDFs subidos. |
| `FRONTEND_DIST_DIR` | Ruta | `/app/frontend/dist` | No | Ruta al bundle HTML/JS/CSS compilado por Vite. |

> [!CAUTION]
> **Seguridad de Secretos:**  
> Los archivos `.env` y `backend/.env` están excluidos deliberadamente mediante `.gitignore`, `.dockerignore` y `.gcloudignore`. Nunca subas claves de API a repositorios de código. En Cloud Run, las variables se inyectan en tiempo de ejecución o vinculándolas a **Secret Manager**.

---

## 📦 4. El Proceso de Construcción Multi-Stage (`Dockerfile`)

El archivo `Dockerfile` del repositorio implementa una estrategia multi-etapa que optimiza el tamaño de la imagen final y previene la presencia de herramientas de compilación innecesarias en producción:

```dockerfile
# ETAPA 1: Node.js 20 Alpine (Frontend Builder)
# Compila TypeScript + Vite + Tailwind CSS -> frontend/dist/
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# ETAPA 2: Python 3.11 Slim (Runtime Final de Producción)
FROM python:3.11-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
WORKDIR /app/backend
COPY backend/pyproject.toml backend/uv.lock ./
RUN uv pip install --system --no-cache -r pyproject.toml
COPY backend/src/ ./src/
COPY backend/data/ ./data/
COPY README.md /app/README.md

# Copia los artefactos del frontend desde la Etapa 1
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')" || exit 1

ENTRYPOINT ["uvicorn", "src.presentation.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

### Factores clave de este build:
1. **Gestor `uv`:** Las dependencias de Python se instalan en segundos de forma determinista usando el lockfile `uv.lock`.
2. **Caché Inteligente:** Las instrucciones `COPY package.json` y `COPY pyproject.toml` van antes del código fuente, permitiendo a Docker reutilizar capas cacheadas si las dependencias no han cambiado.
3. **Resolución Dinámica de Rutas:** El módulo `backend/src/infrastructure/config.py` detecta si está corriendo dentro del contenedor (`/app/frontend/dist`) o en modo desarrollo local (`../../frontend/dist`).

---

## ☁️ 5. Despliegue en Google Cloud Run (Paso a Paso)

El despliegue en Google Cloud Run se realiza directamente mediante el comando `gcloud run deploy` aprovechando **Cloud Build** para compilar la imagen en la infraestructura de Google (sin consumir recursos locales de CPU o RAM).

### Paso 1: Configurar Proyecto Activo
```bash
gcloud config set project yisussapps
```

### Paso 2: Desplegar el Servicio
Ejecuta el siguiente comando desde la raíz del repositorio (`/home/soyisuss/Documents/rag-docs`):

```bash
gcloud run deploy aeco-rag \
    --source . \
    --region us-central1 \
    --platform managed \
    --ingress all \
    --allow-unauthenticated \
    --min-instances 0 \
    --max-instances 2 \
    --memory 1Gi \
    --set-env-vars GEMINI_API_KEY="[TU_GEMINI_KEY]",QDRANT_URL="[TU_QDRANT_URL]",QDRANT_API_KEY="[TU_QDRANT_KEY]",QDRANT_COLLECTION="documents"
```

### Explicación de las banderas críticas:
- `--source .`: Empaqueta el directorio actual, evalúa `.gcloudignore` y lo envía a Cloud Build para ejecutar el `Dockerfile`.
- `--region us-central1`: Región geográfica del servicio (usualmente alineada a la región del cluster de Qdrant para mínima latencia de red).
- `--allow-unauthenticated`: Permite que la interfaz web sea accesible públicamente por los usuarios finales.
- `--min-instances 0`: Configura el escalado a cero (cuando no hay peticiones, las instancias se apagan para no incurrir en gastos).
- `--max-instances 2`: Limita el número máximo de instancias concurrentes para prevenir gastos imprevistos.
- `--memory 1Gi`: Asigna 1 Gigabyte de memoria RAM, ideal para la extracción de texto con PyMuPDF y el procesamiento de fragmentos.

### Paso 3: Re-despliegues Posteriores (Actualizaciones de Código)
Para desplegar nuevas versiones después de realizar cambios en el frontend o backend, las variables de entorno ya quedan registradas en Cloud Run. Solo necesitas ejecutar:

```bash
gcloud run deploy aeco-rag \
    --source . \
    --region us-central1 \
    --platform managed \
    --ingress all \
    --allow-unauthenticated \
    --min-instances 0 \
    --max-instances 2 \
    --memory 1Gi
```

---

## 🐳 6. Despliegue Local / Servidor On-Premise con Docker

Si deseas correr la aplicación en tu máquina local o en una máquina virtual Linux (Ubuntu/Debian) mediante Docker Engine:

### Paso 1: Preparar archivo de entorno
Asegúrate de tener un archivo `.env` configurado dentro de `backend/`:
```bash
cat backend/.env
```
Debe contener:
```env
GEMINI_API_KEY=tu_clave_de_gemini
QDRANT_URL=https://tu-cluster.cloud.qdrant.io
QDRANT_API_KEY=tu_token_qdrant
QDRANT_COLLECTION=documents
```

### Paso 2: Construir la Imagen
```bash
docker build -t yael-bot .
```

### Paso 3: Detener Contenedores Anteriores en el Puerto 8080
Si el puerto 8080 ya está siendo utilizado por otra instancia:
```bash
# Identificar qué contenedor ocupa el puerto
docker ps --filter "publish=8080"

# Detener y remover contenedor previo si aplica
docker stop yael-bot 2>/dev/null || true
docker rm yael-bot 2>/dev/null || true
```

### Paso 4: Ejecutar el Contenedor
```bash
docker run -d \
    --name yael-bot \
    --restart unless-stopped \
    -p 8080:8080 \
    --env-file backend/.env \
    yael-bot
```

### Paso 5: Verificar Estado
```bash
# Ver estado del contenedor y healthcheck
docker ps

# Ver logs de arranque de Uvicorn
docker logs -f yael-bot
```

---

## 📊 7. Monitoreo, Diagnóstico y Health Checks

Una vez desplegada la aplicación, cuenta con herramientas integradas para validar su operatividad:

### A. Health Check Automatizado
El endpoint `/health` realiza una verificación activa de conectividad contra el cluster de Qdrant Cloud:
```bash
curl -s https://aeco-rag-844331208004.us-central1.run.app/health
```
**Respuesta esperada:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "collection": "documents"
}
```

### B. Inspección de Documentos Indexados
```bash
curl -s https://aeco-rag-844331208004.us-central1.run.app/api/documents
```
Permite comprobar si los documentos en almacenamiento físico concuerdan con los puntos vectoriales en Qdrant Cloud.

### C. Inspección de Logs en Vivo
* **En Google Cloud Run:**
  ```bash
  gcloud run services logs tail aeco-rag --region us-central1
  ```
* **En Docker Local:**
  ```bash
  docker logs --tail 100 -f yael-bot
  ```

---

## 🛠️ 8. Resolución de Problemas Frecuentes (Troubleshooting)

### 1. `Bind for 0.0.0.0:8080 failed: port is already allocated`
- **Causa:** Otro proceso (un contenedor Docker anterior o una sesión local de FastAPI/Uvicorn) está ocupando el puerto 8080.
- **Solución:**
  ```bash
  # Ver qué proceso local ocupa el puerto
  lsof -i :8080
  # O detener el contenedor anterior
  docker rm -f $(docker ps -q --filter "publish=8080")
  ```

### 2. `HTTP 405 Method Not Allowed` al hacer `curl -I https://...`
- **Causa:** `curl -I` envía una petición HTTP `HEAD`. FastAPI por defecto registra la ruta raíz como `@app.get("/")`.
- **Solución:** Las peticiones de navegadores web ordinarias envían `GET` y reciben el archivo `index.html` con código `200 OK`. Utiliza `curl https://...` sin la bandera `-I` para verificar la respuesta completa.

### 3. `429 RESOURCE_EXHAUSTED` de Gemini API
- **Causa:** Se ha superado la cuota por minuto (RPM) o por día en Google AI Studio para el modelo `gemini-3.8-flash` o `gemini-embedding-001`.
- **Solución:** Revisa la cuota de tu cuenta en [Google AI Studio Console](https://aistudio.google.com/) o utiliza una clave API con facturación habilitada.

### 4. `qdrant_client.http.exceptions.UnexpectedResponse: 401 Unauthorized`
- **Causa:** El token `QDRANT_API_KEY` o la URL en `QDRANT_URL` son inválidos o han expirado.
- **Solución:** Genera una nueva API Key en la consola de Qdrant Cloud y actualiza las variables de entorno con `gcloud run services update aeco-rag --update-env-vars QDRANT_API_KEY="nuevo_token"`.

### 5. `Cloud Build: Step #0 failed: ... node_modules not found`
- **Causa:** `.dockerignore` o `.gcloudignore` tienen reglas que excluyen accidentalmente archivos críticos como `frontend/package.json` o `frontend/src/`.
- **Solución:** Verifica que en `.gcloudignore` y `.dockerignore` únicamente se excluyan `frontend/node_modules/` y `frontend/dist/`, garantizando que el código fuente sea copiado al contenedor de compilación.

---

## ✅ 9. Lista de Verificación Pre-Despliegue (Checklist)

Antes de promover un nuevo commit o desplegar a Cloud Run, realiza esta comprobación rápida:

- [ ] **Frontend Compila Sin Advertencias:**
  ```bash
  cd frontend && npm run build && cd ..
  ```
- [ ] **Dependencias Python en Sincronía:**
  ```bash
  cd backend && uv lock && cd ..
  ```
- [ ] **Tests / Imports Limpios:**
  ```bash
  python3 -c "from src.presentation.main import app; print('App loaded successfully')"
  ```
- [ ] **Variables de Entorno Verificadas:** Claves activas para Gemini y Qdrant.
- [ ] **Filtros `.gcloudignore` y `.dockerignore`:** Archivos `.env` excluidos de la subida a Cloud Build.
- [ ] **Despliegue y Validación Post-Launch:**
  - `GET /health` devuelve `{"status":"healthy"}`.
  - La interfaz abre limpiamente en el navegador sin parpadeo blanco ni errores de carga en consola JS.
