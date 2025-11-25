/**
 * ErrorHandler Service
 * Centralized error handling with user-friendly messages
 * Prevents technical detail leakage while maintaining debugging capability
 */

import type { Request, Response, NextFunction } from 'express';

/**
 * Custom error classes with status codes
 */
export class ValidationError extends Error {
  constructor(
    message: string,
    public field?: string,
    public statusCode: number = 400
  ) {
    super(message);
    this.name = 'ValidationError';
  }
}

export class RateLimitError extends Error {
  constructor(
    message: string,
    public retryAfterSeconds: number = 60,
    public statusCode: number = 429
  ) {
    super(message);
    this.name = 'RateLimitError';
  }
}

export class TimeoutError extends Error {
  constructor(
    message: string,
    public statusCode: number = 504
  ) {
    super(message);
    this.name = 'TimeoutError';
  }
}

export class APIClientError extends Error {
  constructor(
    message: string,
    public statusCode: number = 502,
    public code: string = 'EXTERNAL_API_ERROR'
  ) {
    super(message);
    this.name = 'APIClientError';
  }
}

export class InternalServerError extends Error {
  constructor(
    message: string,
    public statusCode: number = 500,
    public code: string = 'INTERNAL_ERROR'
  ) {
    super(message);
    this.name = 'InternalServerError';
  }
}

/**
 * Error handler middleware for Express
 * Converts errors to user-friendly API responses
 */
export function errorHandlerMiddleware(
  error: Error,
  _req: Request,
  res: Response,
  _next: NextFunction
): void {
  const errorResponse = handleError(error);

  res.status(errorResponse.statusCode).json({
    success: false,
    error: {
      code: errorResponse.code,
      message: errorResponse.message,
      ...(errorResponse.details && { details: errorResponse.details }),
      ...(errorResponse.field && { field: errorResponse.field }),
    },
    timestamp: new Date().toISOString(),
  });
}

/**
 * Convert error to structured API error response
 */
export function handleError(error: Error): {
  statusCode: number;
  code: string;
  message: string;
  field?: string;
  details?: Record<string, any>;
} {
  // Handle custom error types
  if (error instanceof ValidationError) {
    return {
      statusCode: error.statusCode,
      code: 'VALIDATION_ERROR',
      message: error.message,
      field: error.field,
    };
  }

  if (error instanceof RateLimitError) {
    return {
      statusCode: error.statusCode,
      code: 'RATE_LIMIT_EXCEEDED',
      message: 'Too many requests. Please try again later.',
      details: { retryAfterSeconds: error.retryAfterSeconds },
    };
  }

  if (error instanceof TimeoutError) {
    return {
      statusCode: error.statusCode,
      code: 'REQUEST_TIMEOUT',
      message: 'Request took too long. Please try again.',
    };
  }

  if (error instanceof APIClientError) {
    return {
      statusCode: error.statusCode,
      code: error.code,
      message: 'External service temporarily unavailable. Please try again later.',
    };
  }

  if (error instanceof InternalServerError) {
    return {
      statusCode: error.statusCode,
      code: error.code,
      message: 'An unexpected error occurred. Please try again later.',
    };
  }

  // Handle standard Error
  if (error instanceof Error) {
    // Log error for debugging (in production, this would go to a proper logger)
    console.error('Unhandled error:', {
      name: error.name,
      message: error.message,
      stack: error.stack,
    });

    // Return generic error response to prevent information leakage
    return {
      statusCode: 500,
      code: 'INTERNAL_ERROR',
      message: 'An unexpected error occurred. Please try again later.',
    };
  }

  // Handle unknown error type
  console.error('Unknown error type:', error);
  return {
    statusCode: 500,
    code: 'INTERNAL_ERROR',
    message: 'An unexpected error occurred. Please try again later.',
  };
}

/**
 * Validate concept input and throw ValidationError with specific field
 */
export function validateConceptInput(
  concept: string | undefined,
  depth: string | undefined,
  language: string | undefined
): void {
  if (!concept) {
    throw new ValidationError('Concept is required', 'concept', 400);
  }

  if (!depth || !['intro', 'intermediate', 'advanced'].includes(depth)) {
    throw new ValidationError(
      'Depth must be "intro", "intermediate", or "advanced"',
      'depth',
      400
    );
  }

  if (!language || !['en', 'ja'].includes(language)) {
    throw new ValidationError('Language must be "en" or "ja"', 'language', 400);
  }
}

/**
 * Validate export options and throw ValidationError
 */
export function validateExportOptions(
  conceptId: string | undefined,
  format: string | undefined
): void {
  if (!conceptId) {
    throw new ValidationError('Concept ID is required', 'conceptId', 400);
  }

  if (!format || !['glb', 'json', 'svg'].includes(format)) {
    throw new ValidationError('Format must be "glb", "json", or "svg"', 'format', 400);
  }
}

/**
 * Create timeout error with context
 */
export function createTimeoutError(operation: string, timeoutMs: number): TimeoutError {
  return new TimeoutError(
    `${operation} exceeded ${timeoutMs}ms timeout`,
    504
  );
}

/**
 * Create rate limit error with retry after
 */
export function createRateLimitError(retryAfterSeconds: number): RateLimitError {
  return new RateLimitError(
    'Too many requests. Please try again later.',
    retryAfterSeconds,
    429
  );
}

/**
 * Create external API error
 */
export function createAPIClientError(service: string, statusCode: number): APIClientError {
  const message = statusCode === 401 || statusCode === 403
    ? `${service} authentication failed`
    : `${service} temporarily unavailable`;

  return new APIClientError(message, statusCode > 500 ? 502 : statusCode);
}
