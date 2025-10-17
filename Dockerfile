# =============================
#   STAGE 1 — BUILDER
# =============================
FROM python:3.13-slim AS builder

# Instala o Poetry (sem criar o virtualenv automaticamente)
ENV POETRY_VERSION=2.1.4 \
    POETRY_VIRTUALENVS_CREATE=false \
    PYTHONUNBUFFERED=1
# Instala o Poetry e dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends build-essential curl && \
    pip install --no-cache-dir "poetry==$POETRY_VERSION" && \
    rm -rf /var/lib/apt/lists/*

# Define o diretório de trabalho
WORKDIR /app

# Copia os arquivos do Poetry primeiro (para aproveitar cache)
COPY pyproject.toml poetry.lock ./

# Instala as dependências do projeto (sem o código ainda)
RUN poetry install --no-root --only main -vvv

# Copia o restante da aplicação
COPY . .

# =============================
#   STAGE 2 — RUNTIME
# =============================
FROM python:3.13-slim AS runtime

# Define variáveis de ambiente
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH"

# Instala dependências do sistema + Java 17 (JDK)
RUN apt-get update && apt-get install -y \
    openjdk-21-jre-headless \
    curl \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copia do builder apenas as dependências já instaladas
COPY --from=builder /usr/local/lib/python3.13/site-packages/ /usr/local/lib/python3.13/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# Copia o código-fonte
COPY --from=builder /app /app

# Porta que o app vai escutar
EXPOSE 8000

# Comando de inicialização — Gunicorn com workers Uvicorn
# Ajuste o módulo conforme seu app (ex: "main:app" se for FastAPI)
CMD ["gunicorn", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000" ,"app.main:app"]