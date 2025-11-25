/**
 * Express Application Setup
 * Configures middleware, routes, error handling, and global settings
 */

import express, { Express, Request, Response, NextFunction } from 'express';
import cors from 'cors';
import helmet from 'helmet';
import { v4 as uuidv4 } from 'uuid';
import { errorHandlerMiddleware } from '@/services/ErrorHandler';
import { rateLimiterMiddleware } from '@/middleware/RateLimiter';

/**
 * Create and configure Express application
 */
export function createApp(): Express {
  const app = express();

  // Trust proxy (important for rate limiting when behind reverse proxy)
  app.set('trust proxy', 1);

  // ============ SECURITY MIDDLEWARE ============
  // Helmet helps secure Express apps by setting various HTTP headers
  app.use(
    helmet({
      contentSecurityPolicy: {
        directives: {
          defaultSrc: ["'self'"],
          scriptSrc: ["'self'", "'unsafe-inline'"], // Three.js requires inline scripts
          styleSrc: ["'self'", "'unsafe-inline'"],
          imgSrc: ["'self'", 'data:', 'https:'],
        },
      },
      frameguard: { action: 'deny' }, // Prevent clickjacking
      noSniff: true, // Prevent MIME type sniffing
      xssFilter: true, // Enable XSS filter in IE
    })
  );

  // CORS configuration
  const corsOptions = {
    origin: process.env.CORS_ORIGIN || 'http://localhost:5173',
    credentials: true,
    methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'Authorization', 'X-Session-ID'],
    maxAge: 3600, // 1 hour
  };

  app.use(cors(corsOptions));

  // ============ REQUEST PARSING MIDDLEWARE ============
  // Parse JSON request bodies (limit: 1MB to prevent abuse)
  app.use(express.json({ limit: '1mb' }));

  // Parse URL-encoded form data (limit: 1MB)
  app.use(express.urlencoded({ limit: '1mb', extended: true }));

  // ============ SESSION & REQUEST TRACKING MIDDLEWARE ============
  // Generate or use provided session ID
  app.use((req: Request, res: Response, next: NextFunction) => {
    const sessionId = req.headers['x-session-id'] as string;
    req.headers['x-session-id'] = sessionId || uuidv4();

    // Add request ID for tracing
    const requestId = uuidv4();
    res.set('X-Request-ID', requestId);

    next();
  });

  // ============ RATE LIMITING MIDDLEWARE ============
  // Apply rate limiting (10 requests per minute per session)
  app.use(
    rateLimiterMiddleware({
      windowMs: parseInt(process.env.RATE_LIMIT_WINDOW_MS || '60000', 10),
      maxRequests: parseInt(process.env.RATE_LIMIT_MAX_REQUESTS || '10', 10),
      keyGenerator: (req: Request) => {
        return (req.headers['x-session-id'] as string) || req.ip || 'unknown';
      },
    })
  );

  // ============ LOGGING MIDDLEWARE ============
  // Simple request logging (in production, use Pino or similar)
  app.use((req: Request, res: Response, next: NextFunction) => {
    const startTime = Date.now();
    const sessionId = req.headers['x-session-id'] as string;

    res.on('finish', () => {
      const duration = Date.now() - startTime;
      console.log(`[${sessionId}] ${req.method} ${req.path} ${res.statusCode} ${duration}ms`);
    });

    next();
  });

  // ============ HEALTH CHECK ENDPOINT ============
  app.get('/health', (_req: Request, res: Response): void => {
    res.status(200).json({
      status: 'ok',
      timestamp: new Date().toISOString(),
      uptime: process.uptime(),
    });
  });

  // ============ API ROUTES ============
  // Routes will be added via app.use() in index.ts
  // This is designed to be modular and allow easy route additions

  // ============ 404 HANDLER ============
  app.use((_req: Request, res: Response): void => {
    res.status(404).json({
      success: false,
      error: {
        code: 'NOT_FOUND',
        message: 'Endpoint not found',
      },
      timestamp: new Date().toISOString(),
    });
  });

  // ============ ERROR HANDLER MIDDLEWARE ============
  // Must be last middleware in the chain
  app.use(errorHandlerMiddleware);

  return app;
}

/**
 * Export app creation function for use in index.ts
 */
export default createApp;
