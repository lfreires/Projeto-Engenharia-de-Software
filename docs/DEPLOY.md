# Deploy no Render com Supabase

O DocAI e publicado por uma Blueprint Render a partir da branch
`render-deploy`. A Blueprint cria um unico web service Docker gratuito que
serve a SPA e a API FastAPI no mesmo dominio.

## Dependencias Externas

Antes de criar a Blueprint:

1. Crie um projeto gratuito no Supabase.
2. Copie uma connection string PostgreSQL compativel com aplicacoes externas,
   preferencialmente a string do Supavisor para ambientes IPv4.
3. Crie uma chave Groq para resposta da LLM.
4. Crie uma chave Gemini API para embeddings.

O Render nao cria o projeto Supabase nem essas chaves.

## Criar A Blueprint

1. Envie a branch `render-deploy` para o GitHub.
2. No Render Dashboard, selecione `New > Blueprint`.
3. Conecte este repositorio e selecione o arquivo `render.yaml`.
4. Preencha os segredos solicitados:

| Variavel | Valor |
| --- | --- |
| `DATABASE_URL` | Connection string do Supabase Postgres/Supavisor |
| `GROQ_API_KEY` | Chave da API Groq |
| `GEMINI_API_KEY` | Chave da Gemini API |

5. Confirme a criacao do Blueprint.

O primeiro startup cria a extensao `pgvector`, aplica as tabelas e indexa o
documento demonstrativo. O site fica pronto para consultar `proj-demo` com o
token demonstrativo ja incorporado ao frontend.

## Recursos Criados

| Provedor | Recurso | Uso |
| --- | --- | --- |
| Render | Web Service Docker Free | SPA e API no mesmo hostname |
| Supabase | Postgres Free + `pgvector` | Dados e vetores persistentes |
| Gemini | `gemini-embedding-001` | Embeddings de documentos e buscas |
| Groq | Chat completions | Respostas RAG |

Nao ha API gateway, Terraform, workflows GitHub Actions ou banco Render nesta
arquitetura. O Render monitora `GET /health` e faz auto-deploy dos commits na
branch configurada.

## Verificacao Pos-Deploy

Verifique:

```text
GET /health
GET /api/v1/projects/proj-demo
GET /api/v1/projects/proj-demo/materials
POST /api/v1/query/chat
```

O frontend deve carregar o material `architecture.md` e responder perguntas
sobre Render, Supabase, Gemini ou Groq citando o documento seed.

## Limites Do Nivel Gratuito

- O web service gratuito do Render pode dormir por inatividade e apresentar
  cold start.
- O projeto Supabase gratuito pode pausar apos periodo sem atividade.
- Gemini e Groq estao sujeitos a suas cotas gratuitas.
- O token `dev-token` e adequado apenas para demonstracao publica do MVP.

## Desenvolvimento Local

```bash
cd backend
python -m pip install -r requirements.txt -r requirements-dev.txt
uvicorn app.main:app --reload --port 8000

cd ../frontend
npm ci
npm run dev
```

Sem `DATABASE_URL`, o backend local utiliza memoria e embeddings
deterministicos. Para validar a integracao real, configure `DATABASE_URL`,
`GEMINI_API_KEY` e `GROQ_API_KEY` em `backend/.env`.

## Referencias

- Render Blueprints: <https://render.com/docs/blueprint-spec>
- Render Free Web Services: <https://render.com/free>
- Supabase pgvector: <https://supabase.com/docs/guides/database/extensions/pgvector>
- Gemini Embeddings: <https://ai.google.dev/gemini-api/docs/embeddings>
