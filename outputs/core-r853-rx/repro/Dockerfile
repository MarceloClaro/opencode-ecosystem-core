# syntax=docker/dockerfile:1
# Container de deploy da reprodução (SPEC-935-R882) — engine `stub` por padrão.
# Contexto de build: outputs/core-r853-rx/repro  (precisa de backend/ + frontend/ + serve.py)
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    RX_ENGINE=stub \
    RX_HOST=0.0.0.0 \
    RX_ADMIN_DB=/data/admin.db

WORKDIR /app

# Dependências primeiro (cache de camada).
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# Código + front. app.py resolve FRONTEND como <repro>/frontend (irmão de backend/).
COPY serve.py ./serve.py
COPY backend/ ./backend/
COPY frontend/ ./frontend/

# Persistência (SQLite). Em Render, monte um Disk em /data p/ durar entre deploys.
RUN mkdir -p /data

EXPOSE 8799

# Healthcheck respeitando $PORT quando o provedor o injeta.
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import os,urllib.request,sys; p=os.environ.get('PORT','8799'); sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:'+p+'/health', timeout=4).status==200 else 1)"

CMD ["python", "serve.py"]
