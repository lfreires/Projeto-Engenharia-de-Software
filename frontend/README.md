# DocAI Frontend

SPA React/Vite do DocAI. No deploy Render, ela e compilada pelo `Dockerfile`
raiz e entregue pelo mesmo processo FastAPI que atende `/api/v1/*`.

## Configuracao

| Variavel | Uso |
| --- | --- |
| `VITE_PROJECT_ID` | Projeto aberto por padrao; deploy usa `proj-demo` |
| `VITE_BEARER_TOKEN` | Token demonstrativo; deploy usa `dev-token` |

Nao existe URL de gateway no build: chamadas usam caminhos same-origin como
`/api/v1/query/chat`.

## Desenvolvimento

```bash
npm ci
npm run dev
```

O proxy do Vite direciona `/api` para um backend local em
`http://localhost:8000`.

## Validacao

```bash
npm run build
```
