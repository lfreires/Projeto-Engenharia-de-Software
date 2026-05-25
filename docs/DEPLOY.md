# Deploy no Render com Supabase

O DocAI e publicado por uma Blueprint Render a partir da branch
`render-deploy`. A Blueprint cria dois recursos gratuitos:

- `docai`: Web Service Docker que executa a API FastAPI.
- `docai-frontend`: Static Site Vite que chama a API publica.

## Rotacionar Segredos Expostos

Nunca registre chaves Groq, Google ou a senha Postgres no repositorio. Caso
tenham sido compartilhadas em logs ou conversas, revogue/rotacione as chaves e
redefina a senha do banco antes do novo deploy.

## Corrigir A Conexao Supabase

O host direto `db.<project-ref>.supabase.co:5432` usa IPv6. O Render nao
consegue alcancar esse endpoint, resultando em `Network is unreachable` no
startup da API.

No dashboard Supabase:

1. Abra `Connect`.
2. Selecione **Session pooler** (recomendado para este backend).
3. Copie a URI com host semelhante a `aws-0-<regiao>.pooler.supabase.com` e
   porta `5432`.
4. Grave essa URI no segredo `DATABASE_URL` do servico `docai`.

O **Transaction pooler** em porta `6543` tambem e compativel com o codigo
atual, que desabilita prepared statements do cliente.

## Criar Ou Sincronizar A Blueprint

1. No Render Dashboard, crie ou sincronize a Blueprint usando `render.yaml`
   da branch `render-deploy`.
2. No servico backend `docai`, configure:

| Variavel | Valor |
| --- | --- |
| `DATABASE_URL` | URI **Session pooler** Supabase/Supavisor |
| `GROQ_API_KEY` | Chave Groq rotacionada |
| `GEMINI_API_KEY` | Chave Google/Gemini rotacionada |

3. Sincronize a Blueprint; o Static Site ja recebe
   `VITE_API_BASE_URL=https://docai-v8qm.onrender.com`, URL publica do backend
   existente.

Se o backend for recriado e ganhar outro subdominio Render, atualize
`VITE_API_BASE_URL` em `render.yaml` e sincronize/deploye novamente o frontend.

## Inicializacao E Verificacao

No primeiro startup bem sucedido, o backend habilita `pgvector`, aplica as
migrations e indexa idempotentemente o documento demonstrativo de `proj-demo`.
O backend aceita origens `*.onrender.com` para o frontend publicado.

Verifique a API:

```text
GET https://<api>.onrender.com/health
GET https://<api>.onrender.com/api/v1/projects/proj-demo
```

Em seguida acesse o Static Site; ele deve listar `architecture.md` e responder
uma pergunta sobre Render ou Supabase citando o documento seed.

## Recursos E Limites

| Provedor | Recurso | Uso |
| --- | --- | --- |
| Render | Web Service Docker Free | API FastAPI |
| Render | Static Site Free | SPA Vite |
| Supabase | Postgres Free + `pgvector` | Dados e vetores |
| Gemini | `gemini-embedding-001` | Embeddings |
| Groq | Chat completions | Respostas RAG |

- O web service gratuito pode dormir por inatividade e apresentar cold start.
- O projeto Supabase gratuito pode pausar apos periodo sem atividade.
- Gemini e Groq estao sujeitos as cotas dos seus planos.
- `dev-token` e autenticacao demonstrativa, nao autenticacao de producao.

## Desenvolvimento Local

```bash
cd backend
python -m pip install -r requirements.txt -r requirements-dev.txt
uvicorn app.main:app --reload --port 8000

cd ../frontend
npm ci
npm run dev
```

Sem `DATABASE_URL`, o backend usa memoria e embeddings deterministicos. Deixe
`VITE_API_BASE_URL` vazio localmente para usar o proxy Vite.

## Referencias

- Render Blueprints: <https://render.com/docs/blueprint-spec>
- Supabase connections: <https://supabase.com/docs/guides/database/connecting-to-postgres>
- Supabase pgvector: <https://supabase.com/docs/guides/database/extensions/pgvector>
- Gemini Embeddings: <https://ai.google.dev/gemini-api/docs/embeddings>
