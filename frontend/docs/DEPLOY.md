# Deploy

O frontend e o Render Static Site `docai-frontend` declarado em
`render.yaml`. O build Vite consome a URL publica do backend publicado pelo
mesmo Blueprint.

Valores de build:

- `VITE_API_BASE_URL=https://<servico-api>.onrender.com`
- `VITE_PROJECT_ID=proj-demo`
- `VITE_BEARER_TOKEN=dev-token`

Como o Render nao fornece automaticamente a URL publica de outro servico para
um build de Static Site, defina `VITE_API_BASE_URL` no dashboard apos a API
receber sua URL publica e execute novo deploy do frontend.
