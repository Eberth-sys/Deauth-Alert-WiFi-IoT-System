# frontend/Dockerfile — imagen del frontend (D4)
# Multi-stage: build con Node (Vite) → sirve estáticos con nginx.
# Contexto de build: ./frontend (usa frontend/.dockerignore de D1).

# ---------- Stage 1: build ----------
FROM node:22-alpine AS build
WORKDIR /app

# Dependencias primero (cache de capas): solo los manifiestos.
COPY package.json package-lock.json ./
RUN npm ci

# Código de la app.
COPY . .

# URLs del backend por BUILD-ARG: Vite las hornea en build-time. Sin hardcode.
# (Limitación conocida: cambiar de backend requiere rebuild de esta imagen.)
ARG VITE_BACKEND_URL=http://localhost:8000
ARG VITE_WS_URL=ws://localhost:8000
ENV VITE_BACKEND_URL=$VITE_BACKEND_URL \
    VITE_WS_URL=$VITE_WS_URL

RUN npm run build                        # genera /app/dist

# ---------- Stage 2: serve (nginx) ----------
FROM nginx:1.27-alpine

# Config con SPA fallback (reemplaza el default.conf).
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Estáticos ya compilados.
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80
