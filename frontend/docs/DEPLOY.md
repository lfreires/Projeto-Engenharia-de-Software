# Deploy

O frontend e o Render Static Site `docai-frontend` declarado em
`render.yaml`. O build Vite consome a URL publica do backend publicado pelo
mesmo Blueprint.

A Blueprint fixa `repo: https://github.com/lfreires/Projeto-Engenharia-de-Software.git`
para que o servico existente preserve sua URL `docai-frontend-7wym.onrender.com`
sem continuar compilando o antigo repositorio independente.

Valores de build:

- `VITE_API_BASE_URL=https://docai-v8qm.onrender.com`
- `VITE_PROJECT_ID=proj-demo`
- `VITE_BEARER_TOKEN=dev-token`

A URL do backend atualmente provisionado foi registrada na Blueprint para que
o Static Site ja seja construido conectado. Atualize esse valor caso o backend
seja recriado com outro subdominio.

O projeto abre sem material artificial. Para validar a publicacao, abra
**Materiais**, envie um arquivo `PDF`, `DOCX`, `TXT` ou `MD` (ate 10 MB) e
confirme que o texto extraido aparece antes de consultar o chat.
