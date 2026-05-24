FROM node:20-alpine AS frontend-builder

WORKDIR /build
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./

ARG VITE_PROJECT_ID=proj-demo
ARG VITE_BEARER_TOKEN=dev-token
ENV VITE_PROJECT_ID=$VITE_PROJECT_ID
ENV VITE_BEARER_TOKEN=$VITE_BEARER_TOKEN
RUN npm run build

FROM python:3.11-slim

WORKDIR /app
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/app ./app
COPY backend/migrations ./migrations
COPY --from=frontend-builder /build/dist ./frontend-dist

ENV APP_ENV=production
ENV PYTHONUNBUFFERED=1
EXPOSE 10000

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-10000}"]
