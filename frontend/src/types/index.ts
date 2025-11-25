/**
 * Frontend Type Definitions
 * Core types for React components, state management, and API integration
 */

// API Request/Response Types
export interface ConceptPayload {
  concept: string;
  depth: 'intro' | 'intermediate' | 'advanced';
  language: 'en' | 'ja';
}

export interface ConceptResponse {
  id: string;
  explanationText: string;
  animationSpec: Animation3D;
  embedCodeSnippet?: string;
}

export interface ExportOptions {
  format: 'glb' | 'json' | 'svg';
  resolution?: '720p' | '1080p' | '2k';
  includeAnnotations?: boolean;
  includedLayers?: string[];
}

// 3D Animation/Scene Types
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

export interface AnimationClip {
  name: string;
  duration: number;
  tracks: unknown[];
}

// Control State Types
export interface ControlState {
  isPlaying: boolean;
  playbackSpeed: number; // 0.5 to 2.0
  currentTime: number;
  totalDuration: number;
  visibleLayers: Set<string>;
  allLayers: string[];
}

export interface CameraState {
  position: [number, number, number];
  target: [number, number, number];
  fov: number;
  zoom: number;
}

// UI State Types
export interface UIState {
  currentPhase: 'idle' | 'generating' | 'ready' | 'exporting' | 'error';
  selectedDepth: 'intro' | 'intermediate' | 'advanced';
  selectedLanguage: 'en' | 'ja';
  isLoading: boolean;
  error?: UIError;
  showExportModal: boolean;
  showSessionWarning: boolean;
}

export interface UIError {
  code: string;
  message: string;
  details?: Record<string, unknown>;
}

// Concept/Visualization State
export interface ConceptVisualization {
  id: string;
  concept: string;
  depth: 'intro' | 'intermediate' | 'advanced';
  language: 'en' | 'ja';
  explanation: string;
  animation: Animation3D;
  layers: LayerInfo[];
  createdAt: number;
  expiresAt: number;
}

export interface LayerInfo {
  id: string;
  name: string;
  visible: boolean;
  color?: string;
  opacity?: number;
}

// Component Props Types
export interface ConceptInputFormProps {
  onSubmit: (payload: ConceptPayload) => Promise<void>;
  isLoading: boolean;
  selectedDepth: 'intro' | 'intermediate' | 'advanced';
  selectedLanguage: 'en' | 'ja';
  onDepthChange: (depth: 'intro' | 'intermediate' | 'advanced') => void;
  onLanguageChange: (language: 'en' | 'ja') => void;
}

export interface ThreeJSViewerProps {
  animationSpec: Animation3D;
  isLoading: boolean;
  onLayersChange?: (visibleLayers: string[]) => void;
}

export interface ControlsPanelProps {
  controlState: ControlState;
  onPlayPause: () => void;
  onSpeedChange: (speed: number) => void;
  onSeek: (time: number) => void;
  onLayerToggle: (layerId: string) => void;
}

export interface ExportModalProps {
  isOpen: boolean;
  conceptId: string;
  onClose: () => void;
  onExport: (options: ExportOptions) => Promise<void>;
  isExporting: boolean;
  availableLayers: LayerInfo[];
}

export interface ExplanationPanelProps {
  text: string;
  isLoading: boolean;
}

export interface LanguageSwitcherProps {
  currentLanguage: 'en' | 'ja';
  onLanguageChange: (language: 'en' | 'ja') => void;
}

// Error Types
export class ConceptGenerationError extends Error {
  constructor(
    message: string,
    public code: string = 'GENERATION_ERROR',
    public statusCode: number = 500
  ) {
    super(message);
    this.name = 'ConceptGenerationError';
  }
}

export class ExportError extends Error {
  constructor(
    message: string,
    public code: string = 'EXPORT_ERROR',
    public statusCode: number = 500
  ) {
    super(message);
    this.name = 'ExportError';
  }
}

// Utility Types
export type Depth = 'intro' | 'intermediate' | 'advanced';
export type Language = 'en' | 'ja';
export type ExportFormat = 'glb' | 'json' | 'svg';
export type UIPhase = 'idle' | 'generating' | 'ready' | 'exporting' | 'error';

// API Client Types
export interface APIClientConfig {
  baseURL: string;
  timeout?: number;
  retries?: number;
}

export interface APIRequest<T = unknown> {
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
  url: string;
  data?: T;
  headers?: Record<string, string>;
  timeout?: number;
}

export interface APIClientResponse<T = unknown> {
  data: T;
  status: number;
  statusText: string;
  headers: Record<string, string>;
}
