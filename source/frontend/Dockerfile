# Stage 1 — Build
FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

# Stage 2 — Serve via lightweight nginx
FROM nginx:1.25-alpine

COPY --from=builder /app/dist /usr/share/nginx/html

# SPA fallback: all routes → index.html
COPY nginx-spa.conf /etc/nginx/conf.d/default.conf

EXPOSE 3000

CMD ["nginx", "-g", "daemon off;"]
