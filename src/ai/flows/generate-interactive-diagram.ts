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

// Real-world example structure
const RealWorldExampleSchema = z.object({
  technology: z.string().describe('Technology/platform name (e.g., "AWS", "Kubernetes", "Nginx")'),
  name: z.string().describe('Specific product/service name (e.g., "Elastic Load Balancer", "Ingress Controller")'),
  link: z.string().optional().describe('Documentation link'),
});

// Metrics structure
const ComponentMetricsSchema = z.object({
  throughput: z.string().optional().describe('Throughput capacity (e.g., "1000 req/s")'),
  latency: z.string().optional().describe('Response latency (e.g., "10-50ms")'),
  criticality: z.enum(['essential', 'important', 'optional']).optional().describe('Component criticality level'),
});

// Component metadata structure
const DiagramComponentSchema = z.object({
  id: z.string().describe('Unique identifier for the component (e.g., "valve-a", "pump-1")'),
  label: z.string().describe('Display name of the component (e.g., "Main Valve")'),
  description: z.string().describe('1-2 sentence functional description of what this component does'),
  svgSelector: z.string().describe('CSS selector to target the SVG element (e.g., "#valve-a-path", ".pump-group")'),
  category: z.string().describe('Category of component: "control", "input", "output", "process", "sensor"'),
  // NEW: Debugging layers
  detailedExplanation: z.string().optional().describe('2-3 sentence deep explanation of how this component works'),
  inputs: z.array(z.string()).optional().describe('List of inputs this component receives (e.g., ["HTTP request", "Server status"])'),
  outputs: z.array(z.string()).optional().describe('List of outputs this component produces'),
  failureMode: z.string().optional().describe('What happens if this component fails'),
  failureRecovery: z.string().optional().describe('How the system recovers from this component failure'),
  // NEW: Real-world examples
  realWorldExamples: z.array(RealWorldExampleSchema).optional().describe('Real-world implementations of this component'),
  // NEW: Layer/complexity management
  layer: z.enum(['core', 'advanced']).optional().default('core').describe('Complexity layer for component visibility toggle'),
  // NEW: Metrics
  metrics: ComponentMetricsSchema.optional().describe('Performance metrics for this component'),
});

// Animation timing structure
const AnimationTimingSchema = z.object({
  duration: z.number().min(100).max(5000).describe('Animation duration in milliseconds (100-5000ms)'),
  easing: z.string().optional().describe('CSS easing function (e.g., "ease-in-out", "linear")'),
});

// State snapshot for component debugging
const StateSnapshotSchema = z.object({
  componentId: z.string().describe('ID of the component'),
  state: z.enum(['idle', 'processing', 'complete', 'error']).describe('Current state of component'),
  dataIn: z.string().optional().describe('Input data with context (e.g., "HTTP request with payload 1.5MB")'),
  dataOut: z.string().optional().describe('Output data with context (e.g., "Routed to Server-1")'),
  metrics: z.object({
    load: z.number().optional().describe('Load percentage 0-100'),
    latency: z.number().optional().describe('Latency in milliseconds'),
    errors: z.number().optional().describe('Error count'),
  }).optional().describe('Performance metrics for this step'),
});

// Data flow visualization
const DataFlowSchema = z.object({
  fromComponent: z.string().describe('Source component ID'),
  toComponent: z.string().describe('Destination component ID'),
  dataType: z.string().describe('Type of data flowing (e.g., "HTTP request", "Response")'),
  transformation: z.string().optional().describe('Transformation applied (e.g., "Encrypted with key")'),
  isRequired: z.boolean().optional().describe('Whether this is a critical path'),
});

// Step structure with component references
const DiagramStepSchema = z.object({
  id: z.string().describe('Unique step identifier (e.g., "step-1", "phase-initial")'),
  title: z.string().describe('Step title (e.g., "Initial State", "Pressure Release")'),
  description: z.string().describe('Detailed explanation of what happens in this step'),
  activeComponentIds: z.array(z.string()).describe('Array of component IDs that are active/highlighted in this step'),
  animationTiming: AnimationTimingSchema.optional().describe('Animation timing for transitions'),
  // NEW: State snapshots for debugging
  stateSnapshot: z.array(StateSnapshotSchema).optional().describe('Component states at this step'),
  // NEW: Data flow visualization
  dataFlows: z.array(DataFlowSchema).optional().describe('Data flows happening in this step'),
});

// Scenario definition for "what if?" testing
const ScenarioSchema = z.object({
  scenarioName: z.string().describe('Name of the scenario (e.g., "High Traffic Load")'),
  description: z.string().describe('Description of the scenario'),
  impactedComponents: z.array(z.string()).describe('Component IDs affected by this scenario'),
  visualization: z.object({
    highlightComponents: z.array(z.string()).describe('Components to highlight'),
    dimComponents: z.array(z.string()).describe('Components to dim'),
    animationType: z.enum(['overload', 'failure', 'slow', 'bottleneck']).describe('Type of animation'),
  }).describe('Visualization for this scenario'),
  lessonLearned: z.string().describe('What learners should understand from this scenario'),
});

// Comparable concept definition
const ComparableConceptSchema = z.object({
  conceptName: z.string().describe('Related concept name'),
  similarity: z.string().describe('How it is similar'),
  differences: z.string().describe('How it differs'),
  whenToUseEach: z.string().describe('When to use each approach'),
});

// Connection/dependency definition
const ConnectionSchema = z.object({
  fromComponent: z.string().describe('Source component ID'),
  toComponent: z.string().describe('Destination component ID'),
  connectionType: z.enum(['data-flow', 'control-flow', 'feedback']).describe('Type of connection'),
  label: z.string().describe('Label for the connection (e.g., "HTTP Request")'),
  isRequired: z.boolean().describe('Whether this is a critical path'),
});

// Metadata about the diagram
const DiagramMetadataSchema = z.object({
  conceptName: z.string().describe('The concept being explained'),
  totalDuration: z.number().describe('Estimated total duration for simulation in milliseconds'),
  fps: z.number().optional().default(30).describe('Target frames per second for animations'),
});

// Core diagram content with structured components
const DiagramContentSchema = z.object({
  svgContent: z.string().describe('Complete SVG with embedded D3.js and CSS for interactivity'),
  explanation: z.string().describe('Top-level textual explanation of the entire concept'),
  components: z.array(DiagramComponentSchema).describe('Array of interactive components in the diagram'),
  steps: z.array(DiagramStepSchema).describe('Array of sequential steps in the tutorial/simulation'),
  metadata: DiagramMetadataSchema.describe('Metadata about the diagram'),
  // NEW: Learning guidance
  timeEstimates: z.object({
    quickView: z.number().describe('Minutes to watch animations'),
    deepUnderstanding: z.number().describe('Minutes to read all details'),
    masteryChallenges: z.number().optional().describe('Minutes to test knowledge'),
  }).optional().describe('Time estimates for different learning depths'),
  conceptDifficulty: z.number().min(1).max(10).optional().describe('Difficulty level 1-10'),
  prerequisites: z.array(z.string()).optional().describe('Prerequisites for understanding'),
  keyInsights: z.array(z.string()).optional().describe('3-5 key takeaways'),
  // NEW: Scenarios
  scenarios: z.array(ScenarioSchema).optional().describe('What-if scenarios for testing'),
  // NEW: Comparable concepts
  comparableConcepts: z.array(ComparableConceptSchema).optional().describe('Related concepts for comparison'),
  // NEW: Connections/dependencies
  connections: z.array(ConnectionSchema).optional().describe('Component connections for dependency mapping'),
  // NEW: Quality metrics
  qualityScore: z.number().min(0).max(100).optional().describe('AI self-assessment of quality (0-100)'),
  generationNotes: z.array(z.string()).optional().describe('Notes about generation confidence and quality'),
});

const GenerateInteractiveDiagramOutputSchema = z.object({
  diagramData: DiagramContentSchema.describe('Complete interactive diagram with all three layers of interactivity'),
});
export type GenerateInteractiveDiagramOutput = z.infer<typeof GenerateInteractiveDiagramOutputSchema>;
export type DiagramComponent = z.infer<typeof DiagramComponentSchema>;
export type DiagramStep = z.infer<typeof DiagramStepSchema>;
export type DiagramMetadata = z.infer<typeof DiagramMetadataSchema>;
export type DiagramContent = z.infer<typeof DiagramContentSchema>;
export type RealWorldExample = z.infer<typeof RealWorldExampleSchema>;
export type ComponentMetrics = z.infer<typeof ComponentMetricsSchema>;
export type StateSnapshot = z.infer<typeof StateSnapshotSchema>;
export type DataFlow = z.infer<typeof DataFlowSchema>;
export type Scenario = z.infer<typeof ScenarioSchema>;
export type ComparableConcept = z.infer<typeof ComparableConceptSchema>;
export type Connection = z.infer<typeof ConnectionSchema>;

export async function generateInteractiveDiagram(input: GenerateInteractiveDiagramInput): Promise<GenerateInteractiveDiagramOutput> {
  return generateInteractiveDiagramFlow(input);
}

const diagramPrompt = ai.definePrompt({
  name: 'diagramPrompt',
  input: {schema: GenerateInteractiveDiagramInputSchema},
  output: {schema: GenerateInteractiveDiagramOutputSchema},
  prompt: `You are the Interactive Diagram Engine. Generate a single, strictly valid JSON object explaining: {{{concept}}}

**Output Structure:**
{
  "diagramData": {
    "svgContent": "Self-contained <svg> with CSS animations. Use <g id='comp_id'> for all actors. Modern, clean, flat style.",
    "explanation": "2-3 paragraph overview of the concept.",
    "components": [
      {
        "id": "Must match SVG id",
        "label": "Display name",
        "description": "2-3 sentences technical summary",
        "detailedExplanation": "How this component works (2-3 sentences)",
        "realWorldExamples": [{"technology": "AWS", "name": "ALB", "link": "..."}],
        "failureMode": "What breaks",
        "failureRecovery": "How it recovers",
        "inputs": ["Input type 1", "Input type 2"],
        "outputs": ["Output type 1"],
        "layer": "core|advanced",
        "category": "control|input|output|process|sensor",
        "svgSelector": "CSS selector to SVG element"
      }
    ],
    "steps": [
      {
        "id": "step-1",
        "title": "Step name",
        "description": "Narrative of what happens",
        "activeComponentIds": ["comp1", "comp2"],
        "animationTiming": {"duration": 1000, "easing": "ease-in-out"},
        "stateSnapshot": [{"componentId": "comp1", "state": "idle|processing|complete|error", "dataIn": "...", "dataOut": "..."}],
        "dataFlows": [{"fromComponent": "comp1", "toComponent": "comp2", "dataType": "HTTP request", "transformation": "..."}]
      }
    ],
    "scenarios": [
      {
        "scenarioName": "What if X fails?",
        "description": "User action or condition",
        "impactedComponents": ["comp2", "comp3"],
        "visualization": {"highlightComponents": [...], "dimComponents": [...], "animationType": "overload|failure|slow|bottleneck"},
        "lessonLearned": "Key insight from this scenario"
      }
    ],
    "conceptDifficulty": 5,
    "prerequisites": ["Knowledge area 1", "Knowledge area 2"],
    "keyInsights": ["Key insight 1", "Key insight 2"],
    "timeEstimates": {"quickView": 5, "deepUnderstanding": 15, "masteryChallenges": 20},
    "qualityScore": 85,
    "generationNotes": ["Confidence notes"]
  }
}

**Strict Requirements:**
1. JSON ONLY. No markdown, no preamble, no explanation.
2. ALL component IDs in steps/scenarios MUST exist in components array. NO orphaned references.
3. SVG must use CSS @keyframes for movement (moveLeft, moveRight, moveUp, moveDown, pulse, flowRight, flowLeft).
4. Technical depth for software engineers: include protocols, state management, error handling.
5. 5-8 sequential steps showing progression from start to completion.
6. 3-4 "what-if" scenarios testing knowledge and failure modes.
7. Real-world implementations with specific technologies (AWS, Kubernetes, Nginx, etc.).
8. Every step has visible animation or visual change - NO static diagrams.
9. Validate all references before returning.`,
});

/**
 * Retry logic for handling transient network failures
 * Implements exponential backoff with jitter
 */
async function callDiagramPromptWithRetry(
  input: GenerateInteractiveDiagramInput,
  maxRetries: number = 3
): Promise<GenerateInteractiveDiagramOutput> {
  let lastError: Error | null = null;

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      const { output } = await diagramPrompt(input);
      return output!;
    } catch (error) {
      lastError = error instanceof Error ? error : new Error(String(error));

      // Check if error is retryable (network-related)
      const isNetworkError =
        lastError.message.includes('fetch failed') ||
        lastError.message.includes('socket') ||
        lastError.message.includes('ECONNRESET') ||
        lastError.message.includes('UND_ERR_SOCKET');

      if (!isNetworkError || attempt === maxRetries) {
        // Non-retryable error or max retries reached
        throw lastError;
      }

      // Calculate exponential backoff with jitter
      const baseDelay = Math.pow(2, attempt) * 1000; // 1s, 2s, 4s
      const jitter = Math.random() * 1000;
      const delayMs = baseDelay + jitter;

      console.warn(
        `Network error on attempt ${attempt + 1}/${maxRetries + 1}. Retrying in ${Math.round(delayMs)}ms...`,
        lastError.message
      );

      // Wait before retrying
      await new Promise(resolve => setTimeout(resolve, delayMs));
    }
  }

  throw lastError || new Error('Failed to generate diagram after maximum retries');
}

const generateInteractiveDiagramFlow = ai.defineFlow(
  {
    name: 'generateInteractiveDiagramFlow',
    inputSchema: GenerateInteractiveDiagramInputSchema,
    outputSchema: GenerateInteractiveDiagramOutputSchema,
  },
  async input => {
    return callDiagramPromptWithRetry(input, 3);
  }
);
