# Yael Bot 🤖 - Minimalist Corporate Document Intelligence Platform

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/Frontend-React%2018%20%2B%20TypeScript-61DAFB.svg)](https://react.dev/)
[![Tailwind CSS](https://img.shields.io/badge/UI-Tailwind%20CSS-38B2AC.svg)](https://tailwindcss.com/)
[![Qdrant Cloud](https://img.shields.io/badge/Vector%20DB-Qdrant%20Cloud-DC2626.svg)](https://cloud.qdrant.io/)
[![Gemini API](https://img.shields.io/badge/LLM-Gemini%20Flash-0091FF.svg)](https://aistudio.google.com/)
[![Docker](https://img.shields.io/badge/Container-Docker%20Multi--Stage-2496ED.svg)](https://www.docker.com/)
[![UX Audit Score](https://img.shields.io/badge/UX%20Audit-39%2F40%20(97.5%25)-10b981.svg)](./docs/DESIGN.md)

**Yael Bot** es una plataforma RAG (*Retrieval-Augmented Generation*) corporativa de nivel de producción construida bajo principios de **Clean Architecture (Arquitectura Limpia)**. Cuenta con una interfaz web sobria, minimalista y de ultra alto contraste en **React 18 + TypeScript (Vite + Tailwind CSS)** y un backend completamente desacoplado con **FastAPI**, **Qdrant Cloud** y **Google Gemini Flash**.

El sistema entrega respuestas **estrictamente fundamentadas, trazabilidad exacta por archivo y número de página, y guardrails activos que mitigan alucinaciones e impiden el consumo innecesario de tokens**.

---

## 🏛️ 1. Arquitectura del Sistema

```text
                       ┌────────────────────────┐
                       │    Documentos PDF      │
                       └───────────┬────────────┘
                                   │ PyMuPDF (fitz)
                                   ▼
                       ┌────────────────────────┐
                       │  Extracción + Chunking │  -> ChunkMetadata:
                       │  (Ventana + Overlap)   │     - source_document
                       └───────────┬────────────┘     - page_number
                                   │
                                   ▼
                       ┌────────────────────────┐
                       │  gemini-embedding-001  │  (768 dimensiones)
                       └───────────┬────────────┘
                                   │
                                   ▼
                       ┌────────────────────────┐
                       │ Qdrant Cloud (Remoto)  │  (Colección "documents")
                       └───────────┬────────────┘
                                   │
     [Consulta Usuario] ───────────┼──> Embedding Consulta
                                   │
                                   ▼
                       ┌────────────────────────┐
                       │  Búsqueda Top-3 Cosine │
                       └───────────┬────────────┘
                                   │
                    ¿Score Máximo >= Umbral (0.70)?
                  ┌────────────────┴────────────────┐
             (NO) │                                 │ (SÍ)
                  ▼                                 ▼
     "INSUFFICIENT_INFORMATION"           ┌────────────────────────┐
     (Guardrail Activado: Aborta          │ Inyección de Contexto  │
      llamada al LLM, ahorra costes)      │ [Archivo, Página]      │
                                          └───────────┬────────────┘
                                                      │
                                                      ▼
                                          ┌────────────────────────┐
                                          │ Gemini 3.8 Flash Engine│
                                          └───────────┬────────────┘
                                                      │
                                                      ▼
                                          ┌────────────────────────┐
                                          │ FastAPI REST API       │
                                          │ (/api/chat, /docs)     │
                                          └───────────┬────────────┘
                                                      │
                                                      ▼
                                          ┌────────────────────────┐
                                          │ ⚛️ Frontend React + TS │
                                          │ (Minimalista / Zinc)   │
                                          └────────────────────────┘
```

---

## 🧩 2. Principios de Diseño y Capacidades Clave

### A. Clean Architecture (Arquitectura Limpia)
El backend aísla sus responsabilidades en 4 capas concéntricas sin fugas de dependencias:
* **Domain:** Entidades puras (`DocumentChunk`, `Citation`, `AnswerResult`) e interfaces/puertos abstractos (`VectorStorePort`, `LLMPort`, `EmbedderPort`, `DocumentParserPort`). Cero acoplamiento a librerías de infraestructura.
* **Application:** Casos de uso de negocio orquestadores (`AskQuestionUseCase`, `IngestDocumentUseCase`, `DeleteDocumentUseCase`, `ListDocumentsUseCase`).
* **Infrastructure:** Adaptadores a servicios externos (`QdrantStoreAdapter`, `GeminiLLMAdapter`, `GeminiEmbedderAdapter`, `FitzParserAdapter`) y configuración dinámica de rutas (`config.py`).
* **Presentation:** API REST moderna en FastAPI (`routers/chat.py`, `routers/documents.py`), esquemas de validación Pydantic y servido de la SPA compilada.

### B. Interfaz Minimalista Corporativa ("The Executive Dossier")
* **Máxima Claridad y Cero Ruido:** Eliminación de insignias técnicas superfluas, gradientes llamativos y sobrecarga de badges en la barra superior.
* **Paleta Zinc de Ultra Alto Contraste:** Lienzo Obsidian Zinc (`#09090b`), texto primario `#fafafa` (ratio **21:1**), texto secundario `#a1a1aa` (ratio **7.5:1**, superando **WCAG AAA**).
* **Evaluación UX Heurística:** Calificación de **39/40 (97.5%)** en la auditoría basada en las 10 heurísticas de Nielsen y 0 fallos de carga cognitiva.
* **Tarjetas de Citas Verificadas:** Fichas compactas con tipografía monospace de alta legibilidad, revelando documento fuente, número de página y extracto textual verificado.
* **Notificaciones Flotantes (Toast):** Alertas en pantalla no bloqueantes con atributos ARIA accesibles, sustituyendo cualquier diálogo intrusivo.

### C. Prevención Activa de Alucinaciones (Confidence Guardrail)
Si la similitud semántica de los fragmentos recuperados en Qdrant es inferior al umbral configurado (`0.70`), el sistema aborta de inmediato la llamada al LLM y responde indicando que no dispone de suficiente información contextual verificada. Esto previene respuestas inventadas y optimiza costos.

### D. Trazabilidad y Citas Exactas por Página
Cada fragmento indexado conserva metadatos rigurosos (`source_document` y `page_number`). El modelo sintetiza la respuesta citando expresamente cada fuente al final de cada dato (`[Archivo, Página]`) y expone tarjetas interactivas de respaldo con extractos textuales verificados en la interfaz de React.

### E. Gestión Documental Completa (Drag & Drop + Eliminación)
* **Carga:** Permite arrastrar nuevos PDFs desde la interfaz o explorar archivos; se procesan, vectorizan y sincronizan automáticamente con Qdrant Cloud.
* **Eliminación Atómica:** Modal de confirmación accesible con atajo <kbd>Escape</kbd>. El sistema purga tanto el archivo físico como la totalidad de sus vectores asociados en Qdrant Cloud mediante filtrado por metadatos.

---

## 🚀 3. Guía de Ejecución

### Opción A: Contenedor Docker (Recomendado para Producción)

El proyecto incluye un `Dockerfile` multi-stage optimizado que compila la aplicación React en Node.js y la sirve directamente a través de FastAPI con Python 3.11 y `uv`.

```bash
# 1. Construir la imagen Docker
docker build -t yael-bot .

# 2. Ejecutar el contenedor en segundo plano con tus variables de entorno
docker run -d --name yael-bot -p 8080:8080 --env-file backend/.env yael-bot
```

* **Aplicación Web:** [http://localhost:8080](http://localhost:8080)
* **Documentación Interactiva Swagger (OpenAPI):** [http://localhost:8080/docs](http://localhost:8080/docs)
* **Comprobación de Salud:** [http://localhost:8080/health](http://localhost:8080/health)

Para verificar el estado o ver los registros:
```bash
docker ps
docker logs -f yael-bot
```

---

### Opción B: Modo Desarrollo Local (Hot Reload)

#### Prerrequisitos
* Python 3.11+
* [uv](https://docs.astral.sh/uv/) instalado (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
* Node.js 18+ y npm

#### 1. Variables de Entorno
Copia y configura tus credenciales en `backend/.env`:
```env
# Gemini API Key (Google AI Studio)
GEMINI_API_KEY=tu_clave_de_gemini

# Qdrant Vector Database (Cloud Remoto)
QDRANT_URL=https://tu-cluster.cloud.qdrant.io
QDRANT_API_KEY=tu_api_key_de_qdrant
QDRANT_COLLECTION=documents
```

#### 2. Instalar dependencias
```bash
# Backend
cd backend && uv sync && cd ..

# Frontend
cd frontend && npm install && cd ..
```

#### 3. Levantar servicios en desarrollo
Abre dos terminales:

* **Terminal 1 (Backend FastAPI):**
  ```bash
  cd backend
  uv run uvicorn src.presentation.main:app --host 0.0.0.0 --port 8080 --reload
  ```
  Swagger UI: [http://localhost:8080/docs](http://localhost:8080/docs)

* **Terminal 2 (Frontend React + Vite):**
  ```bash
  cd frontend
  npm run dev
  ```
  Accede a la aplicación en: [http://localhost:5173](http://localhost:5173)

---

## 📡 4. Catálogo de Endpoints de la API

| Método | Endpoint | Entrada | Salida | Descripción |
| :--- | :--- | :--- | :--- | :--- |
| **`GET`** | `/health` / `/api/health` | Ninguna | `{ status, version, collection }` | Comprobación de salud y conexión a Qdrant Cloud |
| **`POST`** | `/api/chat` | `{ query, similarity_threshold?, limit? }` | `{ query, answer, max_score, threshold, guardrail_passed, sources, message }` | Consulta RAG con citas y guardrail activo |
| **`GET`** | `/api/documents` | Ninguna | `{ total, documents: [{ name, in_storage, in_vector_store }] }` | Lista de documentos indexados |
| **`POST`** | `/api/documents/upload` | `multipart/form-data` (`files`: PDF[]) | `{ uploaded, total_chunks, message }` | Carga, extracción, chunking y vectorización |
| **`DELETE`**| `/api/documents/{doc_name}` | Path param `doc_name` | `{ document_name, deleted, message }` | Elimina archivo físico y purga vectores en Qdrant |

---

## 🚢 5. Despliegue en Google Cloud Run

El servicio de producción está desplegado en **Google Cloud Run**:

* **Aplicación en Producción:** [https://aeco-rag-844331208004.us-central1.run.app](https://aeco-rag-844331208004.us-central1.run.app)
* **API Docs (Swagger UI):** [https://aeco-rag-844331208004.us-central1.run.app/docs](https://aeco-rag-844331208004.us-central1.run.app/docs)
* **Health Check Endpoint:** [https://aeco-rag-844331208004.us-central1.run.app/health](https://aeco-rag-844331208004.us-central1.run.app/health)
* **Revisión Activa:** `aeco-rag-00005-7vd` (100% del tráfico en `us-central1`)

### Re-despliegue continuo con Cloud Build:
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

Cloud Build procesa automáticamente el `Dockerfile` multi-stage, compila los assets estáticos del frontend de React con Node.js 20, e instala las dependencias optimizadas de Python con `uv` en FastAPI.

> [!TIP]
> **Guía Exhaustiva de Despliegue:**  
> Consulta **[docs/DEPLOYMENT_GUIDE.md](./docs/DEPLOYMENT_GUIDE.md)** para una explicación completa de configuración de variables de entorno, manejo de secretos, permisos IAM de Google Cloud, Docker local y solución de incidencias (troubleshooting).

---

## 📊 6. Estructura del Repositorio

```text
rag-docs/
├── Dockerfile                   # Build multi-stage (Node.js 20 + Python 3.11 / uv)
├── .dockerignore                # Filtro optimizado para Docker
├── .gcloudignore                # Filtro optimizado para Cloud Build
├── .gitignore                   # Filtro para control de versiones Git
├── README.md                    # Documentación global y manual de ejecución
│
├── docs/                        # 📚 DOCUMENTACIÓN TÉCNICA Y COMPLEMENTARIA
│   ├── README.md                # Índice y catálogo de documentos
│   ├── DEPLOYMENT_GUIDE.md      # Guía definitiva de despliegue (Cloud Run & Docker)
│   ├── TRANSITION_STATUS.md     # Bitácora detallada de migración y estado
│   ├── PRODUCT.md               # Verdad durable de producto, posicionamiento y principios
│   └── DESIGN.md                # Sistema de diseño ("The Executive Dossier")
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
