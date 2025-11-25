# Multi-stage build for Node.js backend
FROM node:18-alpine AS builder

WORKDIR /build

# Copy package files
COPY package.json package-lock.json* pnpm-lock.yaml* yarn.lock* ./
COPY backend/package.json ./backend/

# Install dependencies
RUN npm ci --workspace=backend

# Copy source code
COPY backend/src ./backend/src
COPY backend/tsconfig.json ./backend/

# Build TypeScript
RUN npm run build -w backend

# Production image
FROM node:18-alpine

WORKDIR /app

# Install dumb-init for proper signal handling
RUN apk add --no-cache dumb-init

# Copy package files
COPY package.json package-lock.json* ./
COPY backend/package.json ./backend/

# Install production dependencies only
ENV NODE_ENV=production
RUN npm ci --workspace=backend --omit=dev

# Copy built application from builder
COPY --from=builder /build/backend/dist ./backend/dist

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3000/health', (r) => {if (r.statusCode !== 200) throw new Error(r.statusCode)})"

# Security: run as non-root
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001 && \
    chown -R nodejs:nodejs /app

USER nodejs

# Expose port
EXPOSE 3000

# Use dumb-init to handle signals properly
ENTRYPOINT ["/usr/bin/dumb-init", "--"]

# Start application
CMD ["node", "backend/dist/index.js"]
