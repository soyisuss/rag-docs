import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from src.infrastructure import config
from src.presentation.routers.chat import router as chat_router
from src.presentation.routers.documents import router as documents_router
from src.presentation.routers.auth import router as auth_router
from src.presentation.schemas import HealthResponse


def create_app() -> FastAPI:
    app = FastAPI(
        title="Yael Bot - RAG Assistant API",
        description="Clean Architecture REST API for Document RAG with Gemini & Qdrant",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Enable CORS for frontend development and Cloudflare Pages
    allow_origins = config.CORS_ORIGINS if config.CORS_ORIGINS else ["*"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Health check endpoints
    @app.get("/health", response_model=HealthResponse, tags=["Health"])
    @app.get("/api/health", response_model=HealthResponse, tags=["Health"])
    def health_check() -> HealthResponse:
        return HealthResponse(
            status="healthy",
            version="1.0.0",
            collection=config.QDRANT_COLLECTION,
        )

    # API Routers
    app.include_router(chat_router)
    app.include_router(documents_router)
    app.include_router(auth_router)

    # Mount static frontend build if it exists (for unified Cloud Run deployment)
    dist_path = config.FRONTEND_DIST_DIR
    if dist_path.is_dir() and (dist_path / "index.html").is_file():
        # Mount assets
        assets_path = dist_path / "assets"
        if assets_path.is_dir():
            app.mount("/assets", StaticFiles(directory=str(assets_path)), name="assets")

        # Catch-all route for Single Page Application client-side routing
        @app.get("/{full_path:path}", include_in_schema=False)
        def serve_spa(full_path: str):
            requested_file = dist_path / full_path
            if requested_file.is_file():
                return FileResponse(requested_file)
            return FileResponse(dist_path / "index.html")

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.presentation.main:app",
        host=config.HOST,
        port=config.PORT,
        reload=True,
    )
