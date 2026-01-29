/**
 * API client for VisuaLearn backend
 * Handles all communication with the FastAPI server
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface DiagramRequest {
  concept: string;
  educational_level: 'elementary' | 'intermediate' | 'advanced';
}

export interface DiagramPlan {
  concept: string;
  diagram_type: string;
  components: string[];
  relationships: Array<{ from: string; to: string; label: string }>;
  success_criteria: string[];
  educational_level: string;
  key_insights: string[];
}

export interface DiagramMetadata {
  step_times: {
    planning: number;
    generation: number;
    review: number;
    conversion: number;
    storage: number;
  };
  refinement_instructions: string;
  concept: string;
  components_count: number;
  relationships_count: number;
}

export interface DiagramResponse {
  png_filename: string;
  svg_filename: string;
  xml_content: string;
  plan: DiagramPlan;
  review_score: number;
  iterations: number;
  total_time_seconds: number;
  metadata: DiagramMetadata;
}

export interface ErrorResponse {
  error: string;
  message: string;
  details: string;
}

/**
 * Generate a diagram from a concept
 */
export async function generateDiagram(request: DiagramRequest): Promise<DiagramResponse> {
  const response = await fetch(`${API_BASE_URL}/api/diagram`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    let errorData: ErrorResponse;
    try {
      errorData = await response.json();
    } catch {
      errorData = {
        error: 'unknown_error',
        message: `HTTP ${response.status}: ${response.statusText}`,
        details: '',
      };
    }
    throw new APIError(errorData.message, errorData.error, errorData.details);
  }

  return response.json();
}

/**
 * Download a file from the export endpoint
 */
export async function downloadFile(filename: string): Promise<Blob> {
  const response = await fetch(`${API_BASE_URL}/api/export/${encodeURIComponent(filename)}`);

  if (!response.ok) {
    throw new APIError(
      `Failed to download ${filename}`,
      'download_error',
      `HTTP ${response.status}`
    );
  }

  return response.blob();
}

/**
 * Custom error class for API errors
 */
export class APIError extends Error {
  code: string;
  details: string;

  constructor(message: string, code: string, details: string) {
    super(message);
    this.code = code;
    this.details = details;
    this.name = 'APIError';
  }
}

/**
 * Check API health status
 */
export async function checkHealth(): Promise<{ status: string; version: string }> {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    if (!response.ok) {
      throw new Error('Health check failed');
    }
    return response.json();
  } catch (error) {
    throw new APIError(
      'Backend service is unavailable',
      'service_unavailable',
      String(error)
    );
  }
}
