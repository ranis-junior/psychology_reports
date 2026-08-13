# Subindo a aplicação pela primeira vez (ambiente local)

Este guia descreve o passo a passo para configurar e rodar a aplicação localmente.

> **Pré-requisitos:** você precisa ter **PostgreSQL** e **Python** instalados na máquina.

---

## 1. Preparar aplicação e banco de dados

### 1.1. Definir a variável `ENVIRONMENT`

Define qual arquivo de configuração será lido pela aplicação.

```bash
export ENVIRONMENT=dev
```

### 1.2. Instalar dependências

```bash
poetry install --no-root
```

### 1.3. Rodar as migrações do banco

```bash
alembic upgrade head
```

---

## 2. Preparar dependências da aplicação

### 2.1. Subir o armazenamento de objetos (MinIO)

O `docker-compose` já contém a configuração necessária.

```bash
docker compose up -d minio
```

### 2.2. Subir o servidor de cache em memória (Valkey)

```bash
valkey-server
```

Com tudo configurado, já podemos subir a aplicação.

---

## 3. Subir a aplicação FastAPI e o worker

### 3.1. Subir a aplicação

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3.2. Subir o worker

Responsável pelo processamento em paralelo.

```bash
taskiq worker app.main:broker
```

Após isso, a aplicação estará disponível em `http://localhost:8000`.

---

## Comandos úteis

### Poetry

| Comando | Descrição |
|---|---|
| `poetry self add poetry-plugin-up` | Instala o plugin que permite atualizar todos os pacotes de uma vez |
| `poetry up --latest` | Atualiza os pacotes para suas últimas versões |
| `poetry env remove --all` | Remove o virtualenv criado |
| `poetry install --no-root` | Instala as dependências do projeto sem instalar o próprio projeto como dependência |

### Alembic

| Comando | Descrição                                               |
|---|---------------------------------------------------------|
| `alembic init alembic` | Cria a estrutura inicial de pastas                      |
| `alembic revision -m "descrição da mudança"` | Cria uma migração vazia para ser preenchida manualmente |
| `alembic revision --autogenerate -m "descrição da mudança"` | Cria uma nova migração a partir das mudanças nos modelos |
| `alembic upgrade head` | Aplica as mudanças até a mais recente                   |
| `alembic downgrade -1` | Desfaz a última mudança                                 |
| `alembic downgrade base` | Desfaz tudo, volta ao estado inicial (sem tabelas)      |
| `alembic downgrade <revision_id>` | Volta até uma revisão específica                        |
| `alembic current` | Mostra qual revisão está aplicada no banco atualmente   |
| `alembic history --verbose` | Mostra o histórico detalhado de todas as revisões       |
