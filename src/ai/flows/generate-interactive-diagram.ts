'use server';

/**
 * @fileOverview A flow for generating interactive diagrams from a given concept.
 *
 * - generateInteractiveDiagram - A function that generates an interactive diagram explaining a concept.
 * - GenerateInteractiveDiagramInput - The input type for the generateInteractivediagram function.
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

  - The SVG must be interactive.
  - Tutorial steps must correspond to elements in the SVG. Add an 'id' attribute to the SVG elements that are part of the tutorial, following the pattern "step-0", "step-1", etc., corresponding to each step's index. These elements will be highlighted.
  - For interactive components that should have a tooltip, wrap the component and its tooltip text in a group with the class "tooltip-group". Inside this group, the main component should be the first element. Then, add a <rect> with the class "tooltip-overlay" that covers the component's area. Finally, add a <text> element with the class "tooltip-text" for the description. The overlay and text will be shown on hover.
  - The tooltip text should be white and positioned on top of the semi-transparent grey overlay. Explain what the component is and its use.
  - The explanation should provide a general overview of the concept, while the steps provide detailed guidance.
  - Ensure that the generated SVG is well-formed and valid.
  - Make sure that the step by step tutorial is clear, concise and comprehensive and can be used as a guide for the user to understand the concept.
  - All interactive elements that can be highlighted or have tooltips must have the 'interactive-element' class.

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
