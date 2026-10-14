FROM python:3.11-slim

# Install uv for reproducible, fast dependency installation
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set environment variables for non-interactive execution
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080

WORKDIR /app

# Copy dependency specifications first to leverage Docker layer caching
COPY pyproject.toml uv.lock ./

# Install dependencies using uv into system Python
RUN uv pip install --system --no-cache -r pyproject.toml

# Copy application source code and initial structure
COPY src/ ./src/
COPY data/ ./data/
COPY .streamlit/ ./.streamlit/
COPY README.md ./

# Expose Streamlit port
EXPOSE 8080

# Health check
HEALTHCHECK CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/_stcore/health')" || exit 1

# Start Streamlit application
ENTRYPOINT ["streamlit", "run", "src/ui/app.py", "--server.port=8080", "--server.address=0.0.0.0", "--server.headless=true", "--browser.gatherUsageStats=false"]
