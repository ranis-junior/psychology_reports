# =============================
#   STAGE 1 — BUILDER
# =============================
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11 AS builder

# Instala o Poetry (sem criar o virtualenv automaticamente)
ENV POETRY_VERSION=2.1.4 \
    POETRY_VIRTUALENVS_CREATE=false \
    PYTHONUNBUFFERED=1 \
    PIP_EXTRA_INDEX_URL=https://www.piwheels.org/simple
# Instala o Poetry e dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends curl && \
    pip install --no-cache-dir "poetry==$POETRY_VERSION" && \
    rm -rf /var/lib/apt/lists/*

# Define o diretório de trabalho
WORKDIR /app

# Copia os arquivos do Poetry primeiro (para aproveitar cache)
COPY pyproject.toml poetry.lock ./

# Instala as dependências do projeto (sem o código ainda)
RUN poetry install --no-root --only main

# Copia o restante da aplicação
COPY . .

# =============================
#   STAGE 2 — RUNTIME
# =============================
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11 AS runtime

# Define variáveis de ambiente
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH" \
    PIP_EXTRA_INDEX_URL=https://www.piwheels.org/simple

# Instala dependências do sistema + Java 17 (JDK)
RUN apt-get update && apt-get install -y \
    openjdk-21-jre-headless \
    curl \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copia do builder apenas as dependências já instaladas
COPY --from=builder /usr/local /usr/local

# Copia o código-fonte
COPY --from=builder /app /app

# Porta que o app vai escutar
EXPOSE 8000

# Comando de inicialização — Gunicorn com workers Uvicorn
# Ajuste o módulo conforme seu app (ex: "main:app" se for FastAPI)
CMD ["gunicorn", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000" ,"app.main:app"]
