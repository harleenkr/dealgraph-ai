# Stage 1: Build the React Application
FROM node:20-alpine AS builder

WORKDIR /app

# Install dependencies
COPY package.json package-lock.json ./
RUN npm install --legacy-peer-deps

# Copy source code and build
COPY . .
# Hardcoding VITE_API_URL directly in the Docker build step for Vite static compilation
ENV VITE_API_URL="https://dealgraph-backend-266277963066.us-central1.run.app"
RUN npm run build

# Stage 2: Serve with Nginx
FROM nginx:alpine

# Copy the custom Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy the built assets from the builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Cloud Run defaults to 8080
EXPOSE 8080

CMD ["nginx", "-g", "daemon off;"]
