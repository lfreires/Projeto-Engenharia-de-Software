# Deploy

O frontend nao e implantado separadamente. O `Dockerfile` raiz executa o build
Vite e copia `dist/` para a imagem FastAPI publicada pela Blueprint Render.

Valores de build demonstrativos:

- `VITE_PROJECT_ID=proj-demo`
- `VITE_BEARER_TOKEN=dev-token`
