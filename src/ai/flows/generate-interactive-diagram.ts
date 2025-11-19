'use server';

/**
 * @fileOverview A flow for generating interactive diagrams from a given concept.
 *
 * - generateInteractiveDiagram - A function that generates an interactive diagram explaining a concept.
 * - GenerateInteractiveDiagramInput - The input type for the generateInteractiveDiagram function.
 * - GenerateInteractiveDiagramOutput - The return type for the generateInteractiveDiagram function.
 */

import {ai} from '@/ai/genkit';
import {z} from 'genkit';

const GenerateInteractiveDiagramInputSchema = z.object({
  concept: z.string().describe('The concept to generate an interactive diagram for.'),
});
export type GenerateInteractiveDiagramInput = z.infer<typeof GenerateInteractiveDiagramInputSchema>;

const DiagramContentSchema = z.object({
  svgContent: z.string().describe('The SVG content of the interactive diagram.'),
  explanation: z.string().describe('A textual explanation of the diagram and its components.'),
  steps: z.array(z.string()).describe('An array of strings, each representing a step in the tutorial.'),
});

const GenerateInteractiveDiagramOutputSchema = z.object({
  diagramData: DiagramContentSchema.describe('Diagram SVG content and step by step explanation'),
});
export type GenerateInteractiveDiagramOutput = z.infer<typeof GenerateInteractiveDiagramOutputSchema>;

export async function generateInteractiveDiagram(input: GenerateInteractiveDiagramInput): Promise<GenerateInteractiveDiagramOutput> {
  return generateInteractiveDiagramFlow(input);
}

const diagramPrompt = ai.definePrompt({
  name: 'diagramPrompt',
  input: {schema: GenerateInteractiveDiagramInputSchema},
  output: {schema: GenerateInteractiveDiagramOutputSchema},
  prompt: `You are an expert at creating interactive SVG diagrams that clearly and concisely explain complex concepts. 

  The user will provide a concept, and you will respond with:
  1.  An SVG diagram suitable for rendering directly in a browser.
  2.  An explanation of the diagram.
  3.  A step by step tutorial of the concept, with steps described as short and clear bullet points.

  Concept: {{{concept}}}

  Ensure that the SVG diagram is interactive, with components that can be highlighted and animated to demonstrate the concept in real-time. The SVG should have tooltips which explain parts of the diagram. The explanation should provide a general overview of the concept, while the steps provide detailed guidance.

  Ensure that the generated SVG is well-formed and valid.

  Make sure that the step by step tutorial is clear, concise and comprehensive and can be used as a guide for the user to understand the concept.

  Output should conform to this schema: ${JSON.stringify(GenerateInteractiveDiagramOutputSchema.shape, null, 2)}
  `,
});

const generateInteractiveDiagramFlow = ai.defineFlow(
  {
    name: 'generateInteractiveDiagramFlow',
    inputSchema: GenerateInteractiveDiagramInputSchema,
    outputSchema: GenerateInteractiveDiagramOutputSchema,
  },
  async input => {
    const {output} = await diagramPrompt(input);
    return output!;
  }
);
