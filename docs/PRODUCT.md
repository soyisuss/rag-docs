# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

General organizational knowledge base users: employees, analysts, and collaborators across any department who need fast, verified answers from internal manuals, technical briefs, compliance policies, or project documentation without manually searching through long PDFs.

## Product Purpose

Yael Bot is an intelligent document RAG assistant that ingests, indexes, and answers questions against organizational PDF documents. Success means delivering truthful, audit-grade answers with exact page-level citations, eliminating guesswork, and cleanly declining to answer when documents lack sufficient context.

## Positioning

Unlike generic conversational AI bots that summarize loosely or hallucinate missing facts, Yael Bot operates with strict factual grounding and active guardrails (semantic threshold ≥ 0.70). If retrieved context is insufficient, it aborts the LLM call entirely, preventing hallucination, conserving token costs, and providing exact page-level citations for every verified fact.

## Operating Context

Desktop and responsive web browser environments. Users upload PDFs via drag-and-drop, manage their active document library, and consult Yael Bot through an austere, high-contrast minimalist interface. Users expect fast responses, quiet indicators of system readiness, and inspectable citation cards with source document names, page numbers, and verified text excerpts without visual clutter.

## Capabilities and Constraints

- **Capabilities:** PDF upload via drag & drop, text extraction with PyMuPDF (`fitz`), chunking with overlap, dense vector embeddings with `gemini-embedding-001` (768d), remote vector storage in Qdrant Cloud, cosine semantic search, confidence guardrail gating (threshold ≥ 0.70), response synthesis with Gemini Flash, page-level citation extraction, document deletion with atomic physical file and Qdrant vector purging.
- **Constraints:** PDF format only for ingestion; requires external connectivity to Qdrant Cloud and Google Gemini API.
- **Terminology:** "Guardrail activo", "Citas exactas", "Similitud semántica", "Documentos indexados".

## Brand Commitments

- **Name:** Yael Bot (tagline: "Minimalist Corporate Document Intelligence Platform").
- **Voice:** Professional, precise, factual, and objective in Spanish. Never conversational fluff or fabricated certainty.
- **Identity:** Minimalist corporate executive aesthetic ("The Executive Dossier") built on an Obsidian Zinc palette (`#09090b`), hairline architectural dividers (`#27272a`), ultra-high contrast typography (21:1 heading contrast, 7.5:1 body contrast exceeding WCAG AAA), and zero decorative chrome clutter.

## Evidence on Hand

- **Codebase:** Clean Architecture FastAPI backend (`backend/src/`), React 18 + TypeScript + Tailwind CSS frontend (`frontend/src/`).
- **Containerization:** Multi-stage Docker build (`yael-bot`) targeting local Docker and Google Cloud Run.
- **Storage:** Dynamic PDF repository configured under `backend/data/raw/`.

## Product Principles

1. **Audit-Grade Precision over Speculation**: Answers must be strictly grounded in uploaded source materials. If semantic similarity is below 0.70, explicitly decline rather than guess.
2. **Page-Exact Traceability**: Every claim must tie back to its source document and specific page number. Citations are primary interface elements, not footnotes.
3. **Operational Clarity over Visual Noise**: Deliver essential system status and ingestion feedback cleanly without cluttering the workspace with redundant technical badges or decorative chrome.
4. **Frictionless Document Management**: Ingesting and removing knowledge assets should be simple (drag-and-drop, clear deletion confirmation, clean vector cleanup).
