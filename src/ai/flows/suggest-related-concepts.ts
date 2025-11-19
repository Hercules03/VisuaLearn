'use server';

/**
 * @fileOverview Provides suggestions for related concepts to explore after viewing a diagram.
 *
 * - suggestRelatedConcepts - A function that suggests related concepts based on the input concept.
 * - SuggestRelatedConceptsInput - The input type for the suggestRelatedConcepts function.
 * - SuggestRelatedConceptsOutput - The return type for the suggestRelatedConcepts function.
 */

import {ai} from '@/ai/genkit';
import {z} from 'genkit';

const SuggestRelatedConceptsInputSchema = z.object({
  concept: z.string().describe('The concept the user has just viewed.'),
});
export type SuggestRelatedConceptsInput = z.infer<
  typeof SuggestRelatedConceptsInputSchema
>;

const SuggestRelatedConceptsOutputSchema = z.object({
  relatedConcepts: z
    .array(z.string())
    .describe('A list of related concepts to explore next.'),
});
export type SuggestRelatedConceptsOutput = z.infer<
  typeof SuggestRelatedConceptsOutputSchema
>;

export async function suggestRelatedConcepts(
  input: SuggestRelatedConceptsInput
): Promise<SuggestRelatedConceptsOutput> {
  return suggestRelatedConceptsFlow(input);
}

const prompt = ai.definePrompt({
  name: 'suggestRelatedConceptsPrompt',
  input: {schema: SuggestRelatedConceptsInputSchema},
  output: {schema: SuggestRelatedConceptsOutputSchema},
  prompt: `Suggest related concepts to the following concept, so the user can deepen their understanding of the subject:

Concept: {{{concept}}}

Return a list of related concepts.`,
});

const suggestRelatedConceptsFlow = ai.defineFlow(
  {
    name: 'suggestRelatedConceptsFlow',
    inputSchema: SuggestRelatedConceptsInputSchema,
    outputSchema: SuggestRelatedConceptsOutputSchema,
  },
  async input => {
    const {output} = await prompt(input);
    return output!;
  }
);
