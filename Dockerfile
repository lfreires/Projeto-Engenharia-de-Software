# ── Frontend Dockerfile (multi-stage) ────────────────────────────────────────
# Stage 1: build the React/Vite app
FROM node:20-alpine AS builder

WORKDIR /app

# Install dependencies first (layer cache)
COPY package*.json ./
RUN npm ci

# Copy source
COPY . .

# Vite env vars are compile-time — pass them as build args
ARG VITE_PROJECT_ID=ecommerce-api
ARG VITE_BEARER_TOKEN=dev-token
ENV VITE_PROJECT_ID=$VITE_PROJECT_ID
ENV VITE_BEARER_TOKEN=$VITE_BEARER_TOKEN

RUN npm run build

# ── Stage 2: serve with nginx ─────────────────────────────────────────────────
FROM nginx:1.27-alpine

# Copy built assets
COPY --from=builder /app/dist /usr/share/nginx/html

# nginx config with /api/ proxy to backend
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
