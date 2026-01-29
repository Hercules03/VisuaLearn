/**
 * Hook for managing diagram generation state and API calls
 */

import { useState, useCallback } from 'react';
import type {
  DiagramResponse,
  DiagramRequest,
} from '@/lib/api';
import {
  generateDiagram,
  downloadFile,
  APIError,
} from '@/lib/api';

export type GenerationStep = 'analyzing' | 'planning' | 'generating' | 'reviewing' | 'completed' | 'error';

export interface DiagramState {
  isLoading: boolean;
  step: GenerationStep;
  error: string | null;
  response: DiagramResponse | null;
  progress: number; // 0-100
}

export function useDiagram() {
  const [state, setState] = useState<DiagramState>({
    isLoading: false,
    step: 'analyzing',
    error: null,
    response: null,
    progress: 0,
  });

  const generateDiagramWithTracking = useCallback(
    async (request: DiagramRequest) => {
      setState({
        isLoading: true,
        step: 'analyzing',
        error: null,
        response: null,
        progress: 0,
      });

      try {
        // Simulate step progression while API call is in flight
        const progressInterval = setInterval(() => {
          setState((prev) => ({
            ...prev,
            progress: Math.min(prev.progress + Math.random() * 20, 90),
          }));
        }, 500);

        // Call the backend API
        const response = await generateDiagram(request);

        // Clear progress interval
        clearInterval(progressInterval);

        // Complete the progress
        setState({
          isLoading: false,
          step: 'completed',
          error: null,
          response,
          progress: 100,
        });

        return response;
      } catch (error) {
        const errorMessage =
          error instanceof APIError ? error.message : 'An unexpected error occurred';

        setState({
          isLoading: false,
          step: 'error',
          error: errorMessage,
          response: null,
          progress: 0,
        });

        throw error;
      }
    },
    []
  );

  const downloadDiagramFile = useCallback(
    async (filename: string, format: 'png' | 'svg' | 'xml'): Promise<void> => {
      try {
        const blob = await downloadFile(filename);

        // Create download link
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;

        // Set filename with appropriate extension
        const extension = format === 'svg' ? 'svg' : format === 'xml' ? 'xml' : 'png';
        link.download = `diagram.${extension}`;

        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
      } catch (error) {
        const errorMessage =
          error instanceof APIError
            ? error.message
            : `Failed to download ${format.toUpperCase()}`;
        setState((prev) => ({
          ...prev,
          error: errorMessage,
        }));
        throw error;
      }
    },
    []
  );

  const resetState = useCallback(() => {
    setState({
      isLoading: false,
      step: 'analyzing',
      error: null,
      response: null,
      progress: 0,
    });
  }, []);

  return {
    state,
    generateDiagram: generateDiagramWithTracking,
    downloadFile: downloadDiagramFile,
    resetState,
  };
}
