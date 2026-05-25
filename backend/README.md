# DocAI Backend

FastAPI runtime consolidado para o deploy Render. Ele preserva os quatro
prefixos de API do projeto original, atende o Static Site frontend por CORS e
usa Supabase Postgres com `pgvector` em producao.

## Estrutura

```text
app/modules/        routers identity, projects, ingestion e query
app/storage.py      Catalogo/historico em Postgres e MemoryStore local
app/rag.py          loaders, splitters e PGVector via LangChain
app/clients.py      ChatGroq e prompt RAG via LangChain
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

O seed cria somente `proj-demo`, usuario e tokens. Use
`POST /api/v1/ingestion/uploads` (`project_id` + `file`) para indexar arquivos
`PDF`, `DOCX`, `TXT` ou `MD` de ate 10 MB. O texto extraido e persistido para
leitura; o binario enviado nao e armazenado.
Materiais indexados podem ser removidos por
`DELETE /api/v1/projects/{project_id}/materials/{material_id}`; a remocao
elimina o catalogo e os vetores usados pelo retrieval.
