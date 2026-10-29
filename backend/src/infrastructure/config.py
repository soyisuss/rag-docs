import os
from pathlib import Path
from dotenv import load_dotenv

BACKEND_ROOT = Path(__file__).resolve().parent.parent.parent
REPO_ROOT = BACKEND_ROOT.parent

# Load .env file from backend or repo root
load_dotenv(BACKEND_ROOT / ".env")
load_dotenv(REPO_ROOT / ".env")

# Storage configuration
DATA_DIR = Path(os.getenv("DATA_DIR", str(BACKEND_ROOT / "data" / "raw")))

# Resolve frontend dist path
default_dist = REPO_ROOT / "frontend" / "dist"
if not default_dist.exists() and (BACKEND_ROOT / "frontend" / "dist").exists():
    default_dist = BACKEND_ROOT / "frontend" / "dist"

FRONTEND_DIST_DIR = Path(os.getenv("FRONTEND_DIST_DIR", str(default_dist)))

# Gemini configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
GEMINI_EMBEDDING_MODEL = os.getenv("GEMINI_EMBEDDING_MODEL", "gemini-embedding-001")
VECTOR_DIMENSION = int(os.getenv("VECTOR_DIMENSION", "768"))

# Qdrant configuration
QDRANT_URL = os.getenv("QDRANT_URL", "").strip()
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "").strip() or None
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "documents")

# RAG thresholds
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.70"))
TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", "5"))

# Auth / JWT configuration
JWT_SECRET = os.getenv("JWT_SECRET", "yael-bot-jwt-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"

# Server configuration
PORT = int(os.getenv("PORT", "8080"))
HOST = os.getenv("HOST", "0.0.0.0")

# CORS configuration (comma-separated origins or * for open access)
CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "*").split(",")
    if origin.strip()
]
