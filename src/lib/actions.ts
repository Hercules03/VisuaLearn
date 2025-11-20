'use server';

import { generateInteractiveDiagram } from '@/ai/flows/generate-interactive-diagram';
import { suggestRelatedConcepts } from '@/ai/flows/suggest-related-concepts';
import { validateDiagramSchema, getUserFacingErrorMessage } from '@/lib/diagram-validation';
import { z } from 'zod';

const conceptSchema = z.string().min(3, { message: 'Please enter a concept with at least 3 characters.' });

export async function handleGeneration(concept: string) {
  try {
    // Validate input
    const validatedConcept = conceptSchema.safeParse(concept);
    if (!validatedConcept.success) {
      return { error: validatedConcept.error.issues[0].message, diagramData: null, relatedConcepts: null };
    }

    // Generate diagram and related concepts in parallel
    const diagramPromise = generateInteractiveDiagram({ concept: validatedConcept.data });
    const conceptsPromise = suggestRelatedConcepts({ concept: validatedConcept.data });

    const [diagramResult, conceptsResult] = await Promise.all([diagramPromise, conceptsPromise]);

    // Validate diagram result exists
    if (!diagramResult || !diagramResult.diagramData) {
      return {
        error: 'Failed to generate diagram. Please try again.',
        diagramData: null,
        relatedConcepts: null,
      };
    }

    // Validate diagram schema structure
    const validationResult = validateDiagramSchema(diagramResult.diagramData);
    if (!validationResult.valid) {
      const userMessage = getUserFacingErrorMessage(validationResult.error);
      console.error('Diagram validation error:', validationResult.error);
      return {
        error: userMessage,
        diagramData: null,
        relatedConcepts: null,
      };
    }

    // Validate related concepts result
    if (!conceptsResult || !conceptsResult.relatedConcepts) {
      // Related concepts failing is not fatal; continue with diagram only
      console.warn('Failed to generate related concepts, continuing without them');
      return {
        diagramData: diagramResult.diagramData,
        relatedConcepts: [],
        error: null,
      };
    }

    return {
      diagramData: diagramResult.diagramData,
      relatedConcepts: conceptsResult.relatedConcepts,
      error: null,
    };
  } catch (e) {
    console.error('Generation error:', e);
    const errorMessage = e instanceof Error ? e.message : 'An unknown error occurred.';
    // No fallback data - raise error explicitly per project constraints
    return {
      error: `Generation failed: ${errorMessage}`,
      diagramData: null,
      relatedConcepts: null,
    };
  }
}
