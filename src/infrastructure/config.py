import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Storage configuration
DATA_DIR = Path(os.getenv("DATA_DIR", str(PROJECT_ROOT / "data" / "raw")))
FRONTEND_DIST_DIR = Path(os.getenv("FRONTEND_DIST_DIR", str(PROJECT_ROOT / "frontend" / "dist")))

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
TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", "3"))

# Server configuration
PORT = int(os.getenv("PORT", "8080"))
HOST = os.getenv("HOST", "0.0.0.0")
