# ──────────────────────────────────────────────────────────────────────────────
# IsyShell API — Dockerfile Otimizado
# Base: python:3.11-slim (menor superfície de ataque, sem compiladores desnecessários)
# ──────────────────────────────────────────────────────────────────────────────

FROM python:3.11-slim AS base

# Metadados
LABEL maintainer="ISY.ONE Hackathon FMU Tech 2026"
LABEL description="IsyShell API — Orquestrador Automático de Infraestrutura"

# Variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    SCRIPTS_DIR=/opt/isyone/scripts \
    DB_PATH=/data/isyshell.db \
    SCRIPT_TIMEOUT=120

WORKDIR /app

# ── Dependências do sistema (mínimas) ──────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
        bash \
    && rm -rf /var/lib/apt/lists/*

# ── Dependências Python ────────────────────────────────────────────────────────
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# ── Código da aplicação ────────────────────────────────────────────────────────
COPY app/ ./app/

# ── Diretórios de runtime ──────────────────────────────────────────────────────
RUN mkdir -p /data /opt/isyone/scripts

# ── Usuário não-root (boa prática de segurança) ────────────────────────────────
RUN groupadd --gid 1001 isyshell \
    && useradd --uid 1001 --gid isyshell --shell /bin/bash --create-home isyshell \
    && chown -R isyshell:isyshell /app /data

USER isyshell

EXPOSE 8000

# ── Healthcheck ────────────────────────────────────────────────────────────────
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/')" || exit 1

# ── Comando de inicialização ───────────────────────────────────────────────────
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
