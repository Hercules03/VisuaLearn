/**
 * Backend Entry Point
 * Initializes Express server with all middleware and routes
 */

import dotenv from 'dotenv';
import { createApp } from '@/app';
import conceptRoutes from '@/routes/concepts';
import { cleanupExpiredRateLimits } from '@/middleware/RateLimiter';

// Load environment variables
dotenv.config();

// Validate required environment variables
const requiredEnvVars = ['GEMINI_API_KEY', 'SESSION_SECRET'];
const missingEnvVars = requiredEnvVars.filter((env) => !process.env[env]);

if (missingEnvVars.length > 0) {
  console.error(`Missing required environment variables: ${missingEnvVars.join(', ')}`);
  console.error('Please copy backend/.env.example to backend/.env.local and configure it.');
  process.exit(1);
}

// Create Express application
const app = createApp();

// ============ REGISTER ROUTES ============
// Mount API routes
app.use('/api', conceptRoutes);

// ============ SERVER INITIALIZATION ============
const PORT = parseInt(process.env.PORT || '3000', 10);
const HOST = process.env.HOST || '0.0.0.0';

const server = app.listen(PORT, HOST, () => {
  console.log(`
╔════════════════════════════════════════╗
║         visuaLearn Backend Server       ║
╠════════════════════════════════════════╣
║  Status:      ✓ Running                 ║
║  Host:        ${HOST.padEnd(30)}║
║  Port:        ${PORT.toString().padEnd(30)}║
║  Environment: ${(process.env.NODE_ENV || 'development').padEnd(24)}║
║  API Docs:    http://${HOST}:${PORT}/api/docs        ║
║  Health:      http://${HOST}:${PORT}/health         ║
╚════════════════════════════════════════╝
  `);
});

// ============ CLEANUP & MAINTENANCE ============
// Clean up expired rate limit entries every 5 minutes
const cleanupInterval = setInterval(() => {
  cleanupExpiredRateLimits();
}, 5 * 60 * 1000);

// ============ ERROR HANDLING ============
/**
 * Handle unhandled promise rejections
 */
process.on('unhandledRejection', (reason: Error) => {
  console.error('Unhandled Rejection:', reason);
  // In production, this would be sent to error tracking service
});

/**
 * Handle uncaught exceptions
 */
process.on('uncaughtException', (error: Error) => {
  console.error('Uncaught Exception:', error);
  // In production, gracefully shutdown and alert monitoring
  process.exit(1);
});

// ============ GRACEFUL SHUTDOWN ============
/**
 * Handle SIGTERM and SIGINT signals for graceful shutdown
 */
process.on('SIGTERM', () => {
  console.log('SIGTERM signal received: closing HTTP server');

  // Clear cleanup interval
  clearInterval(cleanupInterval);

  // Close server gracefully
  server.close(() => {
    console.log('HTTP server closed');
    process.exit(0);
  });

  // Force shutdown after 10 seconds
  setTimeout(() => {
    console.error('Could not close connections in time, forcing shutdown');
    process.exit(1);
  }, 10 * 1000);
});

process.on('SIGINT', () => {
  console.log('SIGINT signal received: closing HTTP server');

  // Clear cleanup interval
  clearInterval(cleanupInterval);

  // Close server gracefully
  server.close(() => {
    console.log('HTTP server closed');
    process.exit(0);
  });

  // Force shutdown after 10 seconds
  setTimeout(() => {
    console.error('Could not close connections in time, forcing shutdown');
    process.exit(1);
  }, 10 * 1000);
});

export default app;
