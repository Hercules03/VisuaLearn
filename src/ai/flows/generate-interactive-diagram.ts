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
  prompt: `You are an expert educational technologist and frontend developer. Your mission is to create a self-contained, interactive, and animated educational diagram to explain the following concept: {{{concept}}}.

The output must be a single, well-structured SVG file that includes embedded CSS and JavaScript.

**Core Requirements:**

1.  **Overall Explanation:** Provide a concise, top-level explanation of the concept. This will be displayed alongside the diagram.
2.  **Numbered Steps:** Break down the process into a series of clear, numbered steps. Each step should have a corresponding explanation.
3.  **SVG Diagram:** Create a visually appealing and accurate SVG diagram representing the concept.

**SVG Structure and Interactivity Details:**

1.  **Component Tooltips (The "What"):**
    *   For key components, create tooltips that explain what each component is and its function.
    *   To implement this, wrap the component's SVG elements (e.g., \`<path>\`, \`<rect>\`) within a group (\`<g>\`).
    *   This group **MUST** have two attributes:
        *   \`class="tooltip-group"\`
        *   \`data-tooltip-text="[Your concise explanation here]"\`
    *   **Example:** \`<g class="tooltip-group" data-tooltip-text="This is the CPU. It performs calculations."><rect ... /></g>\`
    *   The user-agent stylesheet will handle the hover effect (grey overlay and white text) automatically based on these attributes.

2.  **Step-by-Step Highlighting (The "How"):**
    *   The diagram must visually correspond to the numbered tutorial steps.
    *   For each step, identify the relevant SVG elements that should be highlighted.
    *   Wrap these elements in a group (\`<g>\`) with a unique ID that follows the pattern \`step-N\`, where \`N\` is the zero-based step number.
    *   **Example:** For Step 1 (which is step 0), the group should be: \`<g id="step-0"> ... elements for step 1 ... </g>\`. For Step 2, it will be \`<g id="step-1">\`, and so on.
    *   The application will automatically apply a "highlighted" class to the correct group based on the user's progress.

**Design and Code Standards:**

*   **Styling:** Use clean, modern aesthetics. Employ a clear color palette to differentiate components. Ensure all styling is embedded within a \`<style>\` tag inside the SVG.
*   **Animation:** Use CSS animations or simple embedded JavaScript for any dynamic effects in the full simulation mode.
*   **Responsiveness:** The SVG should be designed to scale gracefully within its container. Use relative units where possible.
*   **Self-Contained:** All necessary CSS and JavaScript **MUST** be embedded within the final SVG file. Do not use external file references.
*   **IDs:** Ensure all element IDs within the SVG are unique.

Your final output must be structured according to the specified JSON schema.
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
