'use server';

import { generateInteractiveDiagram } from '@/ai/flows/generate-interactive-diagram';
import { suggestRelatedConcepts } from '@/ai/flows/suggest-related-concepts';
import { z } from 'zod';

const conceptSchema = z.string().min(3, { message: 'Please enter a concept with at least 3 characters.' });

export async function handleGeneration(concept: string) {
  try {
    const validatedConcept = conceptSchema.safeParse(concept);
    if (!validatedConcept.success) {
      return { error: validatedConcept.error.issues[0].message, diagramData: null, relatedConcepts: null };
    }

    const diagramPromise = generateInteractiveDiagram({ concept: validatedConcept.data });
    const conceptsPromise = suggestRelatedConcepts({ concept: validatedConcept.data });
    
    const [diagramResult, conceptsResult] = await Promise.all([diagramPromise, conceptsPromise]);

    if (!diagramResult || !diagramResult.diagramData) {
      throw new Error('Failed to generate diagram.');
    }
    if (!conceptsResult || !conceptsResult.relatedConcepts) {
      throw new Error('Failed to suggest related concepts.');
    }

    return { 
      diagramData: diagramResult.diagramData, 
      relatedConcepts: conceptsResult.relatedConcepts,
      error: null 
    };
  } catch (e) {
    console.error(e);
    const errorMessage = e instanceof Error ? e.message : 'An unknown error occurred.';
    return { error: `Generation failed: ${errorMessage}`, diagramData: null, relatedConcepts: null };
  }
}
