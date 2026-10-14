import os
import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
from dotenv import load_dotenv

from src.ingestion.models import DocumentChunk
from src.ingestion.parser import extract_chunks_from_pdf
from src.ingestion.indexer import (
    index_documents, 
    delete_document_from_qdrant, 
    get_qdrant_client, 
    DEFAULT_COLLECTION_NAME
)
from src.retrieval.engine import query_rag_engine

load_dotenv()

st.set_page_config(
    page_title="Yael Bot | Asistente de Documentos",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Enterprise Minimalist Styling (Neutral, corporate, human-centered)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        color: #1E293B;
    }

    /* Top bar & title */
    .app-title {
        font-size: 1.55rem;
        font-weight: 600;
        color: #0F172A;
        letter-spacing: -0.02em;
        margin: 0;
        padding-bottom: 0.2rem;
    }
    .app-subtitle {
        font-size: 0.88rem;
        color: #64748B;
        margin-top: 0.15rem;
        margin-bottom: 1.25rem;
        padding-bottom: 0.85rem;
        border-bottom: 1px solid #E2E8F0;
    }

    /* Sidebar styles */
    .sidebar-label {
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        color: #64748B;
        margin-top: 0.9rem;
        margin-bottom: 0.35rem;
    }

    .doc-pill {
        display: block;
        background-color: #F1F5F9;
        color: #334155;
        border-radius: 3px;
        padding: 0.35rem 0.55rem;
        font-size: 0.78rem;
        width: 100%;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        border: 1px solid #E2E8F0;
        margin-bottom: 0.35rem;
    }

    section[data-testid="stSidebar"] div.stButton > button {
        border-radius: 3px;
        padding: 0.25rem 0.45rem;
        font-size: 0.78rem;
        min-height: 28px;
    }

    /* Reference card */
    .doc-reference-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-left: 3px solid #0F172A;
        border-radius: 3px;
        padding: 0.65rem 0.85rem;
        margin-bottom: 0.45rem;
    }
    .doc-reference-meta {
        font-size: 0.74rem;
        font-weight: 600;
        color: #0F172A;
        text-transform: uppercase;
        letter-spacing: 0.03em;
        margin-bottom: 0.2rem;
    }
    .doc-reference-excerpt {
        font-size: 0.82rem;
        color: #475569;
        line-height: 1.45;
    }

    /* No-results friendly message */
    .no-results-box {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 4px;
        padding: 0.9rem 1.1rem;
        color: #475569;
        font-size: 0.875rem;
        line-height: 1.5;
        margin: 0.5rem 0;
    }

    /* Button adjustments */
    div.stButton > button {
        border-radius: 3px;
        font-size: 0.85rem;
        border: 1px solid #CBD5E1;
    }
</style>
""", unsafe_allow_html=True)


def get_available_documents() -> list[str]:
    """Retrieves document names from both the local directory and Qdrant storage."""
    docs = set()
    raw_dir = Path("data/raw")
    if raw_dir.is_dir():
        docs.update([f.name for f in raw_dir.glob("*.pdf")])

    try:
        client = get_qdrant_client()
        if client.collection_exists(collection_name=DEFAULT_COLLECTION_NAME):
            points, _ = client.scroll(
                collection_name=DEFAULT_COLLECTION_NAME,
                limit=300,
                with_payload=["source_document"],
                with_vectors=False,
            )
            for p in points:
                if p.payload and "source_document" in p.payload:
                    docs.add(p.payload["source_document"])
    except Exception:
        pass

    return sorted(list(docs))


def delete_document(doc_name: str) -> None:
    """Removes a document from disk and purges its vectors from Qdrant."""
    file_path = Path("data/raw") / doc_name
    if file_path.is_file():
        file_path.unlink()

    delete_document_from_qdrant(doc_name)


# --- BARRA LATERAL (Biblioteca de Documentos) ---
with st.sidebar:
    st.markdown("### Documentos")
    st.markdown("---")

    st.markdown('<div class="sidebar-label">Documentos disponibles</div>', unsafe_allow_html=True)
    docs = get_available_documents()
    if docs:
        for doc_name in docs:
            col_doc, col_del = st.columns([0.80, 0.20])
            with col_doc:
                st.markdown(f'<div class="doc-pill" title="{doc_name}">{doc_name}</div>', unsafe_allow_html=True)
            with col_del:
                if st.button("🗑️", key=f"del_{doc_name}", help=f"Eliminar {doc_name}"):
                    with st.spinner(f"Eliminando {doc_name}..."):
                        delete_document(doc_name)
                    st.toast(f"Documento '{doc_name}' eliminado.", icon="🗑️")
                    st.rerun()
    else:
        st.caption("No hay documentos en la biblioteca.")

    st.markdown('<div class="sidebar-label">Agregar documentación</div>', unsafe_allow_html=True)
    uploaded_files = st.file_uploader(
        "Cargar archivos PDF:",
        type=["pdf"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )

    if uploaded_files:
        if st.button("Actualizar biblioteca", use_container_width=True):
            raw_dir = Path("data/raw")
            raw_dir.mkdir(parents=True, exist_ok=True)
            added_count = 0

            with st.spinner("Incorporando documentos a la biblioteca..."):
                for uploaded_file in uploaded_files:
                    file_path = raw_dir / uploaded_file.name
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())

                    chunks = extract_chunks_from_pdf(file_path)
                    count = index_documents(chunks)
                    added_count += count

            st.success(f"Biblioteca actualizada correctamente.")
            st.rerun()

# --- PANEL PRINCIPAL DE CONSULTA ---
st.markdown('<h1 class="app-title">Yael Bot</h1>', unsafe_allow_html=True)
st.markdown(
    '<div class="app-subtitle">'
    'Tu asistente inteligente para explorar y consultar documentos con respuestas precisas, citas exactas y prevención de alucinaciones.'
    '</div>', 
    unsafe_allow_html=True
)

if "messages" not in st.session_state:
    st.session_state.messages = []

# Renderizar conversación previa
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

        if msg.get("found_info") is False:
            st.markdown(
                """<div class="no-results-box">
                <b>Nota:</b> No se encontró información concluyente en los documentos disponibles para responder con precisión. 
                Por favor intenta reformular tu consulta.
                </div>""",
                unsafe_allow_html=True
            )
        elif msg.get("sources"):
            with st.expander(f"Documentación de respaldo ({len(msg['sources'])} referencias)"):
                for s in msg["sources"]:
                    st.markdown(
                        f"""<div class="doc-reference-card">
                        <div class="doc-reference-meta">{s['document']} &nbsp;—&nbsp; Página {s['page']}</div>
                        <div class="doc-reference-excerpt">"{s['snippet']}"</div>
                        </div>""",
                        unsafe_allow_html=True
                    )

# Caja de entrada de consultas
if user_prompt := st.chat_input("Pregúntale a Yael Bot sobre tus documentos..."):
    # Registrar y mostrar mensaje de usuario
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    # Procesar con el motor
    with st.chat_message("assistant"):
        with st.spinner("Buscando en los documentos..."):
            result = query_rag_engine(
                query=user_prompt,
                threshold=0.65,
            )

        raw_answer = result.get("answer", "")
        guardrail_passed = result.get("guardrail_passed", True)
        sources = result.get("sources", [])

        if not guardrail_passed or raw_answer == "INSUFFICIENT_INFORMATION":
            user_friendly_response = (
                "No se encontró información suficiente en los documentos disponibles para responder a tu consulta con certeza."
            )
            st.markdown(user_friendly_response)
            st.markdown(
                """<div class="no-results-box">
                <b>Sugerencia:</b> Intenta reformular la consulta o verifica que los documentos pertinentes estén cargados en la biblioteca.
                </div>""",
                unsafe_allow_html=True
            )
            st.session_state.messages.append({
                "role": "assistant",
                "content": user_friendly_response,
                "found_info": False,
                "sources": [],
            })
        else:
            st.markdown(raw_answer)
            if sources:
                with st.expander(f"Documentación de respaldo ({len(sources)} referencias)"):
                    for s in sources:
                        st.markdown(
                            f"""<div class="doc-reference-card">
                            <div class="doc-reference-meta">{s['document']} &nbsp;—&nbsp; Página {s['page']}</div>
                            <div class="doc-reference-excerpt">"{s['snippet']}"</div>
                            </div>""",
                            unsafe_allow_html=True
                        )

            st.session_state.messages.append({
                "role": "assistant",
                "content": raw_answer,
                "found_info": True,
                "sources": sources,
            })
