# DocAI Backend

FastAPI runtime consolidado para o deploy Render. Ele preserva os quatro
prefixos de API do projeto original, atende o Static Site frontend por CORS e
usa Supabase Postgres com `pgvector` em producao.

## Estrutura

```text
app/modules/        routers identity, projects, ingestion e query
app/storage.py      PostgresStore de producao e MemoryStore local
app/clients.py      Gemini embeddings e Groq chat
migrations/         schema PostgreSQL/pgvector versionado
tests/              contratos e fluxos integrados
```

## Execucao Local

```bash
python -m pip install -r requirements.txt -r requirements-dev.txt
python -m pytest
uvicorn app.main:app --reload --port 8000
```

O modo local sem `DATABASE_URL` semeia memoria e gera vetores
deterministicamente. Em producao, use a connection string **Session pooler**
do Supabase: a conexao direta `db.<ref>.supabase.co` depende de IPv6 e nao e
acessivel pelo Render.
