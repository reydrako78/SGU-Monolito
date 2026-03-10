# ─────────────────────────────────────────────────────────────
# Etapa 1 — dependencias (optimiza cache de Docker layers)
# ─────────────────────────────────────────────────────────────
FROM node:20-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci --prefer-offline

# ─────────────────────────────────────────────────────────────
# Etapa 2 — builder (compila el bundle de producción)
# ─────────────────────────────────────────────────────────────
FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

# ─────────────────────────────────────────────────────────────
# Etapa 3 — producción (nginx sirve el SPA estático)
#   - Imagen ~25MB (sin Node.js)
#   - Maneja rutas SPA: redirige 404 → index.html
# ─────────────────────────────────────────────────────────────
FROM nginx:1.25-alpine AS prod
COPY --from=builder /app/dist /usr/share/nginx/html
# Configuración nginx para SPA (redirige todos los 404 → index.html)
RUN printf 'server {\n\
    listen 3000;\n\
    root /usr/share/nginx/html;\n\
    index index.html;\n\
    # Rutas del SPA -> siempre index.html\n\
    location / {\n\
        try_files $uri $uri/ /index.html;\n\
    }\n\
    # Cache de assets compilados\n\
    location /assets/ {\n\
        expires 1y;\n\
        add_header Cache-Control "public, immutable";\n\
    }\n\
    gzip on;\n\
    gzip_types text/css application/javascript application/json image/svg+xml;\n\
    gzip_min_length 1024;\n\
}\n' > /etc/nginx/conf.d/default.conf
EXPOSE 3000
CMD ["nginx", "-g", "daemon off;"]

# ─────────────────────────────────────────────────────────────
# Etapa desarrollo (hot-reload con Vite + HMR)
# ─────────────────────────────────────────────────────────────
FROM node:20-alpine AS dev
WORKDIR /app
# Dependencias se instalan al montar el volumen en el entrypoint
EXPOSE 3000
CMD sh -c "npm install --prefer-offline && npm run dev -- --host 0.0.0.0 --port 3000"

