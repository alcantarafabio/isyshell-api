FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    SCRIPTS_DIR=/opt/isyone/scripts \
    DB_PATH=/data/isyshell.db \
    SCRIPT_TIMEOUT=120

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
        bash \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

RUN mkdir -p /data /opt/isyone/scripts

RUN groupadd --gid 1001 isyshell \
    && useradd --uid 1001 --gid isyshell --shell /bin/bash --create-home isyshell \
    && chown -R isyshell:isyshell /app /data

USER isyshell

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/')" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
