# =============================
#   STAGE 1 — BUILDER
# =============================
FROM python:3.13-slim AS builder

# Configurações do Poetry e PiWheels
ENV POETRY_VERSION=2.1.4 \
    POETRY_VIRTUALENVS_CREATE=false \
    PYTHONUNBUFFERED=1 \
    PIP_EXTRA_INDEX_URL=https://www.piwheels.org/simple \
    PIP_NO_CACHE_DIR=off

# Instala dependências do sistema + Poetry
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && pip install --no-cache-dir "poetry==$POETRY_VERSION" \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copia os arquivos do Poetry
COPY pyproject.toml poetry.lock ./

# Instala dependências (agora usando PiWheels)
RUN poetry install --no-root --only main

# Copia o restante da aplicação
COPY . .

# =============================
#   STAGE 2 — RUNTIME
# =============================
FROM python:3.13-slim AS runtime

# Variáveis de ambiente
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_EXTRA_INDEX_URL=https://www.piwheels.org/simple

# Instala APENAS dependências de runtime necessárias
RUN apt-get update && apt-get install -y \
    openjdk-21-jre-headless \
    # Adicione outras dependências de sistema aqui se necessário
    # tesseract-ocr \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copia as dependências Python instaladas
COPY --from=builder /usr/local/lib/python3.13/site-packages/ /usr/local/lib/python3.13/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# Copia o código-fonte
COPY --from=builder /app /app

EXPOSE 8000

CMD ["gunicorn", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "app.main:app"]