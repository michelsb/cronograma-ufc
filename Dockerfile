# Build stage
FROM python:3.12-slim AS builder

WORKDIR /build

# Instalar build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar e criar wheel de dependências
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip wheel --no-cache-dir --no-deps --wheel-dir /build/wheels -r requirements.txt

# Runtime stage
FROM python:3.12-slim

WORKDIR /app

# Instalar apenas runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    curl \
    && useradd -m -u 1000 appuser \
    && rm -rf /var/lib/apt/lists/*

# Copiar wheels do builder
COPY --from=builder /build/wheels /wheels
COPY --from=builder /build/requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.txt && \
    rm -rf /wheels && \
    pip show pip setuptools wheel | grep -v "Name\|Version" || true

# Copiar código
COPY --chown=appuser:appuser . .

# Executar como usuário não-root
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl --fail http://localhost:8000/health || exit 1

# Expor porta
EXPOSE 8000

# Comando padrão
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
