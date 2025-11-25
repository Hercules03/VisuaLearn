/**
 * Backend Type Definitions
 * Core types for API contracts, entities, and service interfaces
 */

// User Request/Input Types
export interface ConceptRequestPayload {
  concept: string;
  depth: 'intro' | 'intermediate' | 'advanced';
  language: 'en' | 'ja';
}

export interface ExportRequestPayload {
  conceptId: string;
  format: 'glb' | 'json' | 'svg';
  options?: {
    resolution?: '720p' | '1080p' | '2k';
    includeAnnotations?: boolean;
    includedLayers?: string[];
  };
}

// Core Entities
export interface ConceptRequest {
  id: string;
  concept: string;
  depth: 'intro' | 'intermediate' | 'advanced';
  language: 'en' | 'ja';
  timestamp: string; // ISO 8601
}

export interface AnimationClip {
  name: string;
  duration: number;
  tracks: unknown[];
}

export interface Animation3D {
  metadata: {
    version: string;
    type: string;
    generator: string;
  };
  object: unknown; // three.js Object3D
  geometries: unknown[];
  materials: unknown[];
  animations: AnimationClip[];
}

export interface AnimationSpec {
  conceptId: string;
  threejsObject: Record<string, unknown>; // three.js Object3D JSON
  metadata: {
    depth: string;
    concept: string;
    generatedAt: string;
    version?: string;
  };
}

export interface ExplanationText {
  id: string;
  conceptId: string;
  language: 'en' | 'ja';
  originalText: string;
  translatedText: string;
  wordCount: number;
  structure: {
    headings: string[];
    hasLists: boolean;
    hasTables: boolean;
  };
  generatedAt: string;
  translatedAt?: string;
}

export interface ExportPackage {
  id: string;
  conceptId: string;
  format: 'glb' | 'json' | 'svg';
  resolution: '720p' | '1080p' | '2k';
  includeAnnotations: boolean;
  includedLayers: string[];
  fileSize: number;
  fileName: string;
  data?: Buffer | string;
  generatedAt: string;
  expiresAt: string;
}

// API Response Types
export interface APIResponse<T = unknown> {
  success: boolean;
  data?: T;
  error?: APIError;
  timestamp: string;
}

export interface APIError {
  code: string;
  message: string;
  details?: Record<string, unknown>;
  statusCode: number;
}

// Validation Results
export interface ValidationField {
  field: string;
  message: string;
}

export interface ValidationResult {
  valid: boolean;
  errors: ValidationField[];
}

// Service Response Types
export interface ConceptGenerationResponse {
  id: string;
  explanationText: string;
  animationSpec: AnimationSpec;
  embedCodeSnippet?: string;
}

// Type alias for API responses
export type ConceptResponse = ConceptGenerationResponse;

export interface ExportResponse {
  downloadUrl?: string;
  fileName: string;
  fileSize: number;
  expiresAt?: string;
  data?: Buffer;
}

// Cache Types
export interface CacheEntry<T = unknown> {
  key: string;
  value: T;
  expiresAt: number;
  ttl: number;
}

// Rate Limit Types
export interface RateLimitState {
  sessionId: string;
  requestCount: number;
  windowStart: number;
  resetTime: number;
}

// Session Types
export interface SessionData {
  id: string;
  createdAt: number;
  lastAccessedAt: number;
  expiresAt: number;
  ttl: number;
  data: Record<string, unknown>;
}

// Middleware Context
export interface RequestContext {
  sessionId: string;
  userId?: string;
  timestamp: number;
  requestId: string;
}

// Error Types
export class ValidationError extends Error {
  constructor(
    public field: string,
    message: string,
    public statusCode: number = 400
  ) {
    super(message);
    this.name = 'ValidationError';
  }
}

export class APIErrorResponse extends Error {
  constructor(
    public code: string,
    message: string,
    public statusCode: number = 500,
    public details?: Record<string, unknown>
  ) {
    super(message);
    this.name = 'APIError';
  }
}
