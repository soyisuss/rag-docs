# Yael Bot 🤖 - Intelligent Document RAG Assistant

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![Google Cloud Run](https://img.shields.io/badge/Deployed-Cloud%20Run-4285F4.svg)](https://aeco-rag-844331208004.us-central1.run.app)
[![Qdrant Cloud](https://img.shields.io/badge/Vector%20DB-Qdrant%20Cloud-DC2626.svg)](https://cloud.qdrant.io/)
[![Gemini API](https://img.shields.io/badge/LLM-Gemini%20Flash-0091FF.svg)](https://aistudio.google.com/)

**Yael Bot** es un sistema RAG (*Retrieval-Augmented Generation*) de nivel de producción diseñado para consultar colecciones documentales en formato PDF mediante lenguaje natural. Proporciona **respuestas estrictamente fundamentadas, citas exactas por documento y número de página, y guardrails activos contra alucinaciones**.

🌐 **Demo en Producción:** [https://aeco-rag-844331208004.us-central1.run.app](https://aeco-rag-844331208004.us-central1.run.app)

---

## 🏛️ 1. Arquitectura del Sistema

```
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
                   ¿Score Máximo >= Umbral (0.65)?
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
                                         │ Frontend Streamlit     │
                                         │ (Chat, Citas y Gestión)│
                                         └────────────────────────┘
```

---

## 🧩 2. Características y Principios de Diseño

### A. Prevención Activa de Alucinaciones (Confidence Guardrail)
Si la similitud semántica de los fragmentos recuperados en Qdrant es inferior al umbral configurado (`0.65`), el sistema aborta de inmediato la llamada al LLM y responde indicando que no dispone de suficiente información. Esto previene respuestas inventadas y ahorra consumo de tokens.

### B. Trazabilidad y Citas Exactas por Página
Cada fragmento indexado conserva metadatos rigurosos (`source_document` y `page_number`). El modelo sintetiza la respuesta citando expresamente cada fuente al final de cada dato (`[Archivo, Página]`) y expone tarjetas de respaldo con los extractos textuales en la interfaz.

### C. Gestión Completa de Documentos (Carga y Eliminación 🗑️)
- **Carga:** Permite arrastrar nuevos PDFs desde la interfaz; se procesan, vectorizan y sincronizan automáticamente con Qdrant Cloud.
- **Eliminación:** Los usuarios pueden eliminar cualquier documento con un solo clic. El sistema purga tanto el archivo físico como la totalidad de sus vectores asociados en Qdrant Cloud usando filtrado por metadatos.

### D. Base Vectorial 100% en la Nube (Qdrant Cloud)
Arquitectura desacoplada y sin estado (*stateless*): no requiere almacenamiento en disco local, permitiendo que los contenedores en Cloud Run escalen horizontalmente o a cero sin perder vectores ni metadatos.

### E. Stack Ultra-Ligero y Optimizado
Tras una auditoría de sobre-ingeniería, el proyecto eliminó dependencias pesadas innecesarias (LangChain, Ragas, Pydantic, Vertex AI SDK), quedando con **solo 5 dependencias principales**:
`google-genai`, `qdrant-client`, `pymupdf`, `streamlit` y `python-dotenv`.

---

## 🚀 3. Guía de Ejecución Local

### Prerrequisitos
* Python 3.11+
* [uv](https://docs.astral.sh/uv/) instalado (`curl -LsSf https://astral.sh/uv/install.sh | sh`)

### 1. Variables de Entorno
Copia la plantilla de configuración:
```bash
cp .env.example .env
```

Configura tus credenciales en `.env`:
```env
# Gemini API Key (Google AI Studio)
GEMINI_API_KEY=tu_clave_de_gemini

# Qdrant Vector Database (Cloud Remoto)
QDRANT_URL=https://tu-cluster.cloud.qdrant.io
QDRANT_API_KEY=tu_api_key_de_qdrant
QDRANT_COLLECTION=documents
```

### 2. Instalar dependencias
```bash
uv sync
```

### 3. Indexar documentos iniciales
Coloca los archivos PDF en `data/raw/` (o súbelos directamente desde la interfaz web):
```bash
uv run python -m src.ingestion.indexer
```

### 4. Iniciar la Interfaz Web (Streamlit)
```bash
uv run streamlit run src/ui/app.py
```
Abre tu navegador en: [http://localhost:8501](http://localhost:8501).

---

## 🚢 4. Despliegue en Google Cloud Run

El proyecto está preparado para desplegarse como contenedor serverless con escalado a cero (coste $0 cuando no hay tráfico).

### Despliegue directo desde código fuente con Cloud Build:

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

---

## 📊 5. Estructura del Repositorio

```text
├── data/
│   └── raw/                 # PDFs de entrada / biblioteca local
├── src/
│   ├── ingestion/
│   │   ├── models.py        # Dataclasses estándar (ChunkMetadata, DocumentChunk)
│   │   ├── parser.py        # Extracción y chunking por página con PyMuPDF
│   │   └── indexer.py       # Embeddings y sincronización con Qdrant Cloud
│   ├── retrieval/
│   │   └── engine.py        # Motor RAG, Guardrails y síntesis con Yael Bot
│   └── ui/
│       └── app.py           # Frontend Streamlit con citas y eliminación interactiva
├── .dockerignore            # Filtro de exclusión para Docker
├── .gcloudignore            # Optimización de carga para Cloud Build
├── .streamlit/
│   └── config.toml          # Configuración de red y CORS para Cloud Run
├── Dockerfile               # Contenedor optimizado con python:3.11-slim y uv
├── pyproject.toml           # Dependencias limpias gestionadas con uv
└── README.md                # Documentación del proyecto
```
