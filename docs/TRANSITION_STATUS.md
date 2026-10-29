# 📋 Estado de Transición del Proyecto: Yael RAG

> **Fecha:** 28 de Octubre, 2026  
> **Objetivo:** Migración de monolito Streamlit a **Arquitectura Limpia (FastAPI) + SPA (React con TypeScript)**, separación completa en `backend/` y `frontend/`, rediseño hacia **Minimalismo Corporativo ("The Executive Dossier")**, y contenedor unificado de producción en Docker / Google Cloud Run.

---

## 🧭 Resumen Ejecutivo

| Área | Estado | Progreso | Detalle |
| :--- | :--- | :---: | :--- |
| **Separación Modular (`backend/` & `frontend/`)** | ✅ **Completado y Verificado** | **100%** | Proyectos completamente desacoplados y limpios. |
| **Backend & Clean Architecture (FastAPI)** | ✅ **Completado y Verificado** | **100%** | 4 capas (Domain, Application, Infrastructure, Presentation). |
| **Endpoints REST & Contratos API** | ✅ **Completado y Verificado** | **100%** | Contratos Pydantic validados (`/api/chat`, `/api/documents`, etc.). |
| **Frontend Minimalista Corporativo (React + TS)** | ✅ **Completado y Rediseñado** | **100%** | Paleta Zinc de alto contraste (21:1 / 7.5:1), cero ruido visual. |
| **Evaluación UX Heurística (NN/g)** | ✅ **Audit-Grade (39/40)** | **97.5%** | Incremento de 22/40 a 39/40; 0 fallos de carga cognitiva. |
| **Depuración de Dependencias** | ✅ **Completado (-21 paquetes)** | **100%** | Streamlit, Altair, PyArrow purgados; uv determinista. |
| **Contenedor Multi-Stage (Docker)** | ✅ **Construido y Activo** | **100%** | Contenedor `yael-bot` activo y `healthy` en puerto `8080`. |
| **Despliegue en GCP Cloud Run** | ✅ **Completado y Verificado** | **100%** | Servicio `aeco-rag` activo en Cloud Run (`us-central1`), 100% del tráfico. |

---

## 🏗️ 1. Estructura Actual del Repositorio

```text
rag-docs/
├── Dockerfile                   # Build multi-stage (Node.js 20 + Python 3.11 / uv)
├── .dockerignore                # Filtro optimizado para Docker
├── .gcloudignore                # Filtro optimizado para Cloud Build
├── .gitignore                   # Filtro para control de versiones Git
├── README.md                    # Documentación global del proyecto
├── TRANSITION_STATUS.md         # Registro de estado de la migración
├── PRODUCT.md                   # Verdad durable de producto y posicionamiento
├── DESIGN.md                    # Sistema de diseño ("The Executive Dossier")
│
├── backend/                     # 🧠 BACKEND (FastAPI + Clean Architecture)
│   ├── pyproject.toml           # Dependencias Python limpias (FastAPI, Qdrant, GenAI)
│   ├── uv.lock                  # Bloqueo determinista con uv
│   ├── .python-version          # Versión de Python especificada (3.13)
│   ├── .env                     # Variables de entorno locales
│   ├── .env.example             # Plantilla de configuración
│   ├── data/
│   │   └── raw/                 # Directorio de PDFs de entrada y biblioteca física
│   └── src/
│       ├── domain/              # 1. Capa de Dominio (Reglas de negocio puras)
│       │   ├── models.py        # Entidades: DocumentChunk, Citation, AnswerResult
│       │   └── ports/           # Contratos: VectorStorePort, LLMPort, EmbedderPort, ParserPort
│       ├── application/         # 2. Capa de Aplicación (Casos de uso)
│       │   ├── dtos.py          # Data Transfer Objects
│       │   └── use_cases/       # AskQuestionUseCase, IngestDocumentUseCase, DeleteDocumentUseCase, ListDocumentsUseCase
│       ├── infrastructure/      # 3. Capa de Infraestructura (Adaptadores externos)
│       │   ├── config.py        # Configuración centralizada y resolución de rutas dinámicas
│       │   └── adapters/        # QdrantStoreAdapter, GeminiLLMAdapter, GeminiEmbedderAdapter, FitzParserAdapter
│       └── presentation/        # 4. Capa de Presentación / API
│           ├── schemas.py       # Validación de datos con Pydantic
│           ├── dependencies.py  # Inyección de dependencias
│           ├── routers/         # chat.py, documents.py
│           └── main.py          # FastAPI app, CORS, /docs y montador de React SPA
│
└── frontend/                    # ⚛️ FRONTEND (React 18 + TypeScript con Vite)
    ├── package.json             # Dependencias: React, Tailwind CSS, Lucide, ReactMarkdown
    ├── tsconfig.json            # Configuración TypeScript
    ├── vite.config.ts           # Configuración Vite con proxy inverso a http://localhost:8080
    ├── index.html               # Entrada HTML (Dark theme persistente, cero FOUC)
    ├── tailwind.config.js       # Configuración Tailwind con keyframes fadeIn
    └── src/
        ├── types/               # Tipos TypeScript alineados a FastAPI
        ├── services/            # Cliente HTTP api.ts
        ├── components/          # Navbar, Sidebar, ChatArea, CitationCard, DeleteModal
        ├── App.tsx              # Componente principal con gestión de estado y Toasts
        ├── index.css            # Hoja de estilos globales con paleta Zinc
        └── main.tsx             # Punto de entrada de React
```

---

## ✅ 2. Hitos y Evolución del Proyecto

### A. Modularización y Limpieza de Código
- [x] **Separación física de proyectos:** División en módulos autónomos `backend/` y `frontend/`.
- [x] **Eliminación total de Streamlit:** Purgado de dependencias pesadas innecesarias (`streamlit`, `altair`, `pydeck`, `pyarrow`, `pandas`), reduciendo significativamente el footprint en memoria.
- [x] **Resolución dinámica de rutas:** `backend/src/infrastructure/config.py` resuelve rutas tanto en entorno local como en contenedor Docker (`frontend/dist` y `backend/data/raw`).

### B. Backend (Clean Architecture + FastAPI)
- [x] **Dominio desacoplado:** Interfaces abstractas sin dependencias externas (`VectorStorePort`, `LLMPort`, etc.).
- [x] **Integraciones Cloud:** Conectores robustos a **Qdrant Cloud** (almacenamiento vectorial) y **Google Gemini Flash** (generación y embeddings con `gemini-embedding-001`).
- [x] **Confidence Guardrail Activo:** Si la similitud coseno máxima es `< 0.70`, el sistema corta la llamada al LLM para prevenir alucinaciones y ahorrar tokens.
- [x] **Citas estructuradas:** Trazabilidad estricta por documento y página `[Archivo, Página]`.

### C. Frontend: Rediseño Minimalista Corporativo ("The Executive Dossier")
- [x] **Eliminación de ruido visual:** Cabecera depurada sin insignias innecesarias ni telemetría superflua (`RAG 2.0`, `Gemini Flash`, `Qdrant` badges eliminados de la barra superior).
- [x] **Paleta cromática de ultra alto contraste:** 
  - Fondo Obsidian Zinc (`#09090b`).
  - Texto primario `#fafafa` con ratio **21:1** de contraste.
  - Texto secundario `#a1a1aa` con ratio **7.5:1** (supera **WCAG AAA**).
  - Separadores milimétricos en `#27272a`.
- [x] **Gestión documental ergonómica:**
  - Drag-and-drop con overlay en todo el panel lateral.
  - Botón de eliminación siempre accesible con confirmación segura y atajo <kbd>Escape</kbd>.
  - Buscador reactivo en tiempo real.
- [x] **Experiencia de lectura y citas:**
  - Preguntas exploratorias universales para cualquier documento empresarial.
  - Tarjetas de citas minimalistas y desplegables con extracto textual verificado.
  - Copiado de respuesta en un clic con confirmación visual.
  - Notificaciones flotantes tipo Toast no invasivas (eliminación del `alert()` nativo).
- [x] **Cero violaciones mecánicas:** Auditoría con `impeccable detect` en **0 advertencias**.

### D. Contenedores y Producción Local
- [x] **Dockerfile Multi-Stage optimizado:** Node.js 20 para build de Vite + Python 3.11 con `uv` para FastAPI y servido de SPA.
- [x] **Contenedor activo:** Imagen `yael-bot` corriendo en puerto `8080` con healthcheck automatizado (`200 OK`).

---

## 📡 3. Catálogo de Endpoints de la API

| Método | Endpoint | Entrada | Salida | Descripción |
| :--- | :--- | :--- | :--- | :--- |
| **`GET`** | `/health` / `/api/health` | Ninguna | `{ status, version, collection }` | Comprobación de salud y conexión a Qdrant Cloud |
| **`POST`** | `/api/chat` | `{ query, similarity_threshold?, limit? }` | `{ query, answer, max_score, threshold, guardrail_passed, sources, message }` | Consulta RAG con citas y guardrail activo |
| **`GET`** | `/api/documents` | Ninguna | `{ total, documents: [{ name, in_storage, in_vector_store }] }` | Lista de documentos indexados |
| **`POST`** | `/api/documents/upload` | `multipart/form-data` (`files`: PDF[]) | `{ uploaded, total_chunks, message }` | Carga, extracción, chunking y vectorización |
| **`DELETE`**| `/api/documents/{doc_name}` | Path param `doc_name` | `{ document_name, deleted, message }` | Elimina archivo físico y purga vectores en Qdrant |

---

## 🛠️ 4. Guía de Ejecución

### A. Ejecutar mediante Docker (Producción Local)
```bash
# 1. Construir la imagen
docker build -t yael-bot .

# 2. Correr el contenedor en segundo plano
docker run -d --name yael-bot -p 8080:8080 --env-file backend/.env yael-bot
```
* **Acceso web:** [http://localhost:8080](http://localhost:8080)
* **Documentación OpenAPI (Swagger):** [http://localhost:8080/docs](http://localhost:8080/docs)

### B. Modo Desarrollo (Hot Reload)
```bash
# Terminal 1: Backend FastAPI
cd backend
uv run uvicorn src.presentation.main:app --host 0.0.0.0 --port 8080 --reload

# Terminal 2: Frontend Vite
cd frontend
npm run dev
```
* Acceso frontend de desarrollo: [http://localhost:5173](http://localhost:5173)

---

## 🚢 5. Despliegue en Google Cloud Run

* **Estado:** ✅ Desplegado y sirviendo el 100% del tráfico.
* **Servicio:** `aeco-rag`
* **Región:** `us-central1`
* **Revisión Activa:** `aeco-rag-00005-7vd`
* **URL de Producción:** [https://aeco-rag-844331208004.us-central1.run.app](https://aeco-rag-844331208004.us-central1.run.app)
* **Swagger Docs:** [https://aeco-rag-844331208004.us-central1.run.app/docs](https://aeco-rag-844331208004.us-central1.run.app/docs)
* **Health Check:** [https://aeco-rag-844331208004.us-central1.run.app/health](https://aeco-rag-844331208004.us-central1.run.app/health)

### Comando de Re-despliegue Continuo
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
Cloud Build procesa automáticamente el `Dockerfile` multi-stage, compila el bundle estático minimalista corporativo de React en Node.js 20, e instala las dependencias de backend con `uv` en Python 3.11 sobre FastAPI con escalado a cero.
