# DocAI Frontend

SPA React/Vite do DocAI. No Render, ela e publicada como Static Site separado
e chama o Web Service FastAPI pela URL publica configurada no build.

## Configuracao

| Variavel | Uso |
| --- | --- |
| `VITE_API_BASE_URL` | URL publica da API Render; vazio somente localmente |
| `VITE_PROJECT_ID` | Projeto aberto por padrao; deploy usa `proj-demo` |
| `VITE_BEARER_TOKEN` | Token demonstrativo; deploy usa `dev-token` |

No Blueprint atual, `VITE_API_BASE_URL=https://docai-v8qm.onrender.com` conecta
automaticamente o Static Site ao backend existente. O backend permite origens
Static Site `*.onrender.com` via CORS.

No painel **Materiais**, o usuario pode enviar arquivos `PDF`, `DOCX`, `TXT`
ou `MD` de ate 10 MB. A indexacao ocorre durante o envio e o leitor exibe o
texto extraido; o arquivo original nao e armazenado.
Quando esse material ainda nao existe, o botao **Indexar arquitetura original
do DocAI** envia sob demanda o
documento Markdown recuperado do material demonstrativo anterior, descrevendo
a arquitetura Azure planejada. Ele nao e inserido automaticamente no seed.
Materiais ja indexados podem ser excluidos no painel ou no leitor; apos a
confirmacao, o documento deixa de ser utilizado pelo chat.

## Desenvolvimento

```bash
npm ci
npm run dev
```

Com `VITE_API_BASE_URL` vazio, o proxy Vite direciona `/api` para um backend
local em `http://localhost:8000`.

## Validacao

```bash
npm run build
```
