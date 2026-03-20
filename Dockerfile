# Stage 1: Build
FROM node:20-slim AS build

WORKDIR /app

# Copy package files and install
COPY package*.json ./
RUN npm install --legacy-peer-deps

ARG VITE_API_BASE_URL
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

# Copy code and build
COPY . .
RUN npm run build

# Stage 2: Serve
FROM nginx:alpine

# Copy built files
COPY --from=build /app/dist /usr/share/nginx/html

# Copy custom nginx config (optional but recommended for SPA)
RUN echo 'server { \
    listen 80; \
    location / { \
        root /usr/share/nginx/html; \
        index index.html; \
        try_files $uri $uri/ /index.html; \
    } \
}' > /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
