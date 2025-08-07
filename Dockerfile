# Dockerfile for LangChain CLI chatbot - Render optimized
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install UV package manager
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy project configuration and README (required by pyproject.toml)
COPY pyproject.toml uv.lock README.md ./

# Copy application code (new clean structure)
COPY app/ ./app/
COPY packages/ ./packages/

# Install dependencies with UV
RUN uv sync --frozen

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app_user
RUN chown -R app_user:app_user /app
USER app_user

# Expose port (Render automatically assigns PORT environment variable)
EXPOSE 8000

# Health check for new server structure
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# Run the new FastAPI server
CMD ["sh", "-c", "uv run python -m uvicorn app.server:app --host 0.0.0.0 --port ${PORT:-8000}"]
