FROM node:20-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci

COPY . .

ARG VITE_PROJECT_ID=proj-demo
ARG VITE_BEARER_TOKEN=dev-token
ARG VITE_API_BASE_URL=
ENV VITE_PROJECT_ID=$VITE_PROJECT_ID
ENV VITE_BEARER_TOKEN=$VITE_BEARER_TOKEN
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

RUN npm run build

FROM nginx:1.27-alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
