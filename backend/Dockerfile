# ─── Stage 1: Builder ───
FROM python:3.12-slim AS builder

WORKDIR /build

# Install dependencies in a virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ─── Stage 2: Production ───
FROM python:3.12-slim AS production

# Security: run as non-root user
RUN groupadd -r foreman && useradd -r -g foreman foreman

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code
COPY app/ ./app/

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health')" || exit 1

USER foreman

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]