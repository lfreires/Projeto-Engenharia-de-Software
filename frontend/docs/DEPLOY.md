# Deploy

O frontend e o Render Static Site `docai-frontend` declarado em
`render.yaml`. O build Vite consome a URL publica do backend publicado pelo
mesmo Blueprint.

Valores de build:

- `VITE_API_BASE_URL=https://docai-v8qm.onrender.com`
- `VITE_PROJECT_ID=proj-demo`
- `VITE_BEARER_TOKEN=dev-token`

A URL do backend atualmente provisionado foi registrada na Blueprint para que
o Static Site ja seja construido conectado. Atualize esse valor caso o backend
seja recriado com outro subdominio.
