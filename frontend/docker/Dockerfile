# Frontend image: build with Vite, serve with nginx. Build context: frontend/.
FROM node:24-alpine AS build

# Node 24 gives up on IPv4/IPv6 "happy eyeballs" too fast on some Docker networks (ETIMEDOUT).
ENV NODE_OPTIONS=--no-network-family-autoselection
RUN npm install -g pnpm@12.6.0
WORKDIR /app

COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

# Settings come from frontend/.env (copied with the source; Vite reads VITE_* at build time).
COPY . .
RUN pnpm build

FROM nginx:1.27-alpine
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
