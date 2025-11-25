/**
 * RateLimiter Middleware
 * Per-session rate limiting to prevent abuse
 * Default: 10 requests per minute
 */

import type { Request, Response, NextFunction } from 'express';

export interface RateLimitState {
  requests: number;
  resetTime: number;
}

/**
 * In-memory store for rate limit states
 * Maps session ID to rate limit tracking data
 */
const rateLimitStore = new Map<string, RateLimitState>();

/**
 * Configuration for rate limiter
 */
export interface RateLimitConfig {
  windowMs: number; // Time window in milliseconds (default: 60000 = 1 minute)
  maxRequests: number; // Max requests per window (default: 10)
  keyGenerator?: (req: Request) => string; // Function to generate rate limit key
}

/**
 * Default configuration
 */
const defaultConfig: RateLimitConfig = {
  windowMs: 60 * 1000, // 1 minute
  maxRequests: 10,
  keyGenerator: (req: Request): string => {
    // Use session ID if available, otherwise use IP address
    return (req.headers['x-session-id'] as string) || req.ip || 'unknown';
  },
};

/**
 * Create rate limiter middleware
 */
export function rateLimiterMiddleware(config: Partial<RateLimitConfig> = {}): (req: Request, res: Response, next: NextFunction) => void {
  const mergedConfig = { ...defaultConfig, ...config };

  return (req: Request, res: Response, next: NextFunction): void => {
    const key = mergedConfig.keyGenerator!(req);
    const now = Date.now();

    let state = rateLimitStore.get(key);

    // Initialize or reset state if window has expired
    if (!state || now >= state.resetTime) {
      state = {
        requests: 0,
        resetTime: now + mergedConfig.windowMs,
      };
      rateLimitStore.set(key, state);
    }

    // Increment request counter
    state.requests += 1;

    // Calculate remaining time in window
    const remainingMs = state.resetTime - now;
    const retryAfterSeconds = Math.ceil(remainingMs / 1000);

    // Set rate limit headers
    res.set('RateLimit-Limit', mergedConfig.maxRequests.toString());
    res.set('RateLimit-Remaining', Math.max(0, mergedConfig.maxRequests - state.requests).toString());
    res.set('RateLimit-Reset', state.resetTime.toString());

    // Check if limit exceeded
    if (state.requests > mergedConfig.maxRequests) {
      res.set('Retry-After', retryAfterSeconds.toString());
      res.status(429).json({
        success: false,
        error: {
          code: 'RATE_LIMIT_EXCEEDED',
          message: 'Too many requests. Please try again later.',
          details: { retryAfterSeconds },
        },
        timestamp: new Date().toISOString(),
      });
      return;
    }

    next();
  };
}

/**
 * Clean up expired rate limit entries periodically
 * Call this periodically (e.g., every 5 minutes) to prevent memory leaks
 */
export function cleanupExpiredRateLimits(): void {
  const now = Date.now();
  const expiredKeys: string[] = [];

  for (const [key, state] of rateLimitStore.entries()) {
    if (now >= state.resetTime + 60 * 1000) { // Keep entries for 1 minute after reset
      expiredKeys.push(key);
    }
  }

  for (const key of expiredKeys) {
    rateLimitStore.delete(key);
  }
}

/**
 * Get current rate limit state for a key (useful for debugging/monitoring)
 */
export function getRateLimitState(key: string): RateLimitState | undefined {
  return rateLimitStore.get(key);
}

/**
 * Reset rate limit for a specific key (useful for testing or emergency override)
 */
export function resetRateLimit(key: string): void {
  rateLimitStore.delete(key);
}

/**
 * Clear all rate limits
 */
export function clearAllRateLimits(): void {
  rateLimitStore.clear();
}

/**
 * Get statistics about rate limiter state
 */
export function getRateLimitStats(): {
  totalKeys: number;
  activeKeys: number;
  expiredKeys: number;
} {
  const now = Date.now();
  let activeKeys = 0;
  let expiredKeys = 0;

  for (const state of rateLimitStore.values()) {
    if (now < state.resetTime) {
      activeKeys += 1;
    } else {
      expiredKeys += 1;
    }
  }

  return {
    totalKeys: rateLimitStore.size,
    activeKeys,
    expiredKeys,
  };
}
