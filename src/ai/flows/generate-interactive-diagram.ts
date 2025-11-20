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
  prompt: `You are an expert educational technologist and SVG/CSS animation specialist. Your mission is to create a self-contained, interactive, and animated educational diagram to explain the following concept: {{{concept}}}.

**CRITICAL: This diagram must have REAL ANIMATIONS with VISUAL MOVEMENT and FLOW, similar to this reference:**
\`\`\`
- Components actually MOVE between zones/positions during steps (using CSS transforms)
- Messages or data FLOW from one component to another (animated paths, arrows)
- Elements APPEAR and DISAPPEAR with smooth transitions
- Multiple animations happen in sequence (e.g., key moves, then message transforms)
- Hover effects show what each component does
- Step transitions are visually distinct with clear animations
\`\`\`

The output must be a comprehensive interactive diagram with THREE DISTINCT INTERACTION LAYERS:
1. **Component Exploration (The "What"):** Hover over components to see tooltips
2. **Step-by-Step Tutorial (The "How"):** Navigate through sequential steps with animations
3. **Full Simulation Mode (The "Review"):** Auto-play that loops through all steps

**CRITICAL: Component Metadata Structure**

You MUST provide a structured list of all interactive components in the diagram. For EACH component, generate:
- \`id\`: Unique identifier (kebab-case, e.g., "main-valve", "pump-1", "cpu-core")
- \`label\`: Display name (e.g., "Main Valve", "Circulation Pump")
- \`description\`: 1-2 sentence explanation of function
- \`svgSelector\`: CSS selector targeting the element (e.g., "#main-valve", ".pump-group", "[data-component='valve-a']")
- \`category\`: One of: "control", "input", "output", "process", "sensor"

**EXAMPLE Component Structure:**
\`\`\`json
"components": [
  {
    "id": "main-valve",
    "label": "Main Valve",
    "description": "Controls the flow of pressurized fluid through the system.",
    "svgSelector": "#main-valve-group",
    "category": "control"
  },
  {
    "id": "pump",
    "label": "Circulation Pump",
    "description": "Pumps fluid through the circuit under pressure.",
    "svgSelector": "#pump-rect",
    "category": "process"
  }
]
\`\`\`

**CRITICAL: Step Structure**

Break down the process into logical, sequential steps. For EACH step, generate:
- \`id\`: Unique step identifier (e.g., "step-1", "phase-initial")
- \`title\`: Step title (e.g., "Initial State", "Valve Opens")
- \`description\`: Detailed explanation of what happens in this step
- \`activeComponentIds\`: Array of component IDs that are ACTIVE/HIGHLIGHTED in this step (e.g., ["main-valve", "pump"])
  - **CRITICAL CONSTRAINT**: Every ID in \`activeComponentIds\` MUST exist in the \`components\` array
  - **NEVER reference a component ID that you haven't already defined above**
  - If a component isn't in the components array, ADD IT before referencing it in steps
  - Leave empty array [] if no components are active in that step
- \`animationTiming\`: Optional duration (100-5000ms) for the transition

**EXAMPLE Step Structure:**
\`\`\`json
"steps": [
  {
    "id": "step-1",
    "title": "Initial State",
    "description": "The system is at rest. No fluid is flowing. The main valve is closed.",
    "activeComponentIds": [],
    "animationTiming": { "duration": 300 }
  },
  {
    "id": "step-2",
    "title": "Pump Activation",
    "description": "The pump begins operation, building pressure in the system.",
    "activeComponentIds": ["pump"],
    "animationTiming": { "duration": 400 }
  },
  {
    "id": "step-3",
    "title": "Valve Opens",
    "description": "Pressure reaches threshold and opens the main valve, allowing flow.",
    "activeComponentIds": ["pump", "main-valve"],
    "animationTiming": { "duration": 500 }
  }
]
\`\`\`

**EXAMPLE ANIMATION STRUCTURE (MUST FOLLOW THIS PATTERN):**

Your SVG must create the visual effect of components MOVING, FLOWING, and TRANSFORMING across the canvas. Here's the required CSS animation pattern:

\`\`\`css
<style>
  :root {
    --transition-speed: 1.2s;
    --highlight: #FFD700;
    --accent: #FF6B6B;
    --active-opacity: 1;
    --inactive-opacity: 0.3;
  }

  /* ===== POSITION-BASED ANIMATIONS (Components move between zones) ===== */
  @keyframes moveLeft { from { transform: translateX(0); } to { transform: translateX(-200px); } }
  @keyframes moveRight { from { transform: translateX(0); } to { transform: translateX(200px); } }
  @keyframes moveUp { from { transform: translateY(0); } to { transform: translateY(-100px); } }
  @keyframes moveDown { from { transform: translateY(0); } to { transform: translateY(100px); } }

  /* ===== FLOW ANIMATIONS (Data/messages flowing between components) ===== */
  @keyframes flowRight {
    0% { stroke-dashoffset: 20; }
    100% { stroke-dashoffset: 0; }
  }
  @keyframes flowLeft {
    0% { stroke-dashoffset: 20; }
    100% { stroke-dashoffset: 0; }
  }

  /* ===== STATE CHANGE ANIMATIONS ===== */
  @keyframes transformState {
    0% { opacity: 0.5; filter: brightness(0.8); }
    50% { opacity: 0.8; }
    100% { opacity: 1; filter: brightness(1.2); }
  }

  @keyframes slideInFromLeft {
    from { opacity: 0; transform: translateX(-50px); }
    to { opacity: 1; transform: translateX(0); }
  }

  @keyframes slideInFromRight {
    from { opacity: 0; transform: translateX(50px); }
    to { opacity: 1; transform: translateX(0); }
  }

  @keyframes pulse {
    0%, 100% { opacity: 1; filter: brightness(1); }
    50% { opacity: 0.7; filter: brightness(1.3); }
  }

  /* ===== BASE TRANSITIONS ===== */
  [data-step-active] {
    transition: opacity 0.4s ease, fill 0.4s ease, stroke 0.4s ease, filter 0.4s ease;
  }

  /* Group containers that can animate */
  [data-animated-group] {
    transform-origin: center;
  }

  /* ===== STEP-BASED STATE ===== */
  /* When component is ACTIVE in current step */
  [data-step-active="true"] {
    opacity: var(--active-opacity);
    fill: var(--highlight);
    stroke: var(--accent);
    filter: brightness(1.3) drop-shadow(0 0 8px var(--highlight));
  }

  /* When component is INACTIVE */
  [data-step-active="false"] {
    opacity: var(--inactive-opacity);
    fill: #E0E0E0;
    stroke: #AAAAAA;
    filter: brightness(1);
  }

  /* ===== MOVEMENT STATES (Use these to move components between positions) ===== */
  [data-position="start"] {
    transform: translateX(0) translateY(0);
  }

  [data-position="moving"] {
    animation: moveRight var(--transition-speed) ease-in-out forwards;
  }

  [data-position="end"] {
    transform: translateX(200px) translateY(0);
  }

  /* ===== FLOW INDICATORS (Animated paths/arrows showing data flow) ===== */
  [data-flow="true"] {
    stroke-dasharray: 10, 5;
    animation: flowRight 2s linear infinite;
  }

  [data-flow="reverse"] {
    stroke-dasharray: 10, 5;
    animation: flowLeft 2s linear infinite;
  }

  /* ===== TRANSFORMATION INDICATORS (Component changing state) ===== */
  [data-transforming="true"] {
    animation: transformState 0.8s ease-in-out forwards;
  }

  /* ===== HOVER EFFECTS ===== */
  [data-component-hover="true"] {
    opacity: 1 !important;
    fill: var(--highlight) !important;
    filter: brightness(1.5) drop-shadow(0 0 15px var(--highlight)) !important;
    animation: pulse 1.5s ease-in-out infinite;
  }
</style>
\`\`\`

**KEY ANIMATION CONCEPTS TO IMPLEMENT:**
1. **Position-Based Animation**: Components in zones that shift position use \`data-position\` attribute with translate transforms
2. **Flow Animation**: Connections/arrows use \`data-flow="true"\` with stroke-dasharray for moving pattern effect
3. **State Transformation**: When component changes state (e.g., plaintext→ciphertext), use \`data-transforming="true"\`
4. **Sequential Effects**: Each step should trigger animations that give sense of progression and causality

**SVG Structure Requirements (CRITICAL for animations to work):**

1. **Component Organization with Zones:**
   - Organize your SVG into logical "zones" or "areas" using \`<g>\` groups
   - Example: Left zone for "sender", middle zone for "channel", right zone for "receiver"
   - Use visual boundaries (dashed rectangles) to show these zones
   - Components should be positioned within these zones for clarity

2. **Component IDs and Attributes:**
   - Every interactive component MUST have:
     - An ID or matching selector (e.g., \`id="message-component"\`)
     - \`data-step-active="true"|"false"\` attribute for highlighting
     - \`data-component-hover="true"|"false"\` attribute for hover effects
   - Example: \`<g id="grp-message" data-step-active="false" data-component-hover="false">\`

3. **Animation Data Attributes:**
   - Add \`data-position="start"|"moving"|"end"\` to components that move between zones
   - Add \`data-flow="true"|"reverse"\` to arrows/connections showing data flow
   - Add \`data-transforming="true"\` to components that change state (e.g., plaintext→encrypted)
   - Add \`data-animated-group\` to groups containing multiple elements that animate together

4. **Connection/Flow Elements:**
   - Create \`<line>\` or \`<path>\` elements for connections between components
   - Use \`stroke-dasharray\` for dashed appearance
   - Apply \`data-flow="true"\` to animate the dash pattern (creates flowing effect)
   - Position arrows in the middle of the canvas to show communication flow

5. **Structural Example:**
   \`\`\`xml
   <svg viewBox="0 0 800 450">
     <!-- Left Zone: Sender -->
     <g id="zone-sender">
       <g id="grp-plaintext" data-step-active="false" data-animated-group>
         <rect.../>
         <text>PLAINTEXT</text>
       </g>
     </g>

     <!-- Center: Communication Channel -->
     <line x1="200" y1="225" x2="600" y2="225" stroke="#334155"/>
     <path id="flow-arrow" d="M 200 225 L 600 225" data-flow="true"/>

     <!-- Right Zone: Receiver -->
     <g id="zone-receiver">
       <g id="grp-keys" data-step-active="false" data-animated-group>
         <rect.../><text>KEY</text>
       </g>
     </g>
   </svg>
   \`\`\`

6. **Step-Based Structure:**
   - Create logical step groups (not necessarily DOM groups, but conceptually)
   - Each step should have distinct visual changes:
     - Step 1: Initialize, show all components faded
     - Step 2: Highlight first component with animation
     - Step 3: Move component or show flow animation
     - Step 4: Transform component (state change)
     - Step 5: Move to next location
   - Each step's active components are set via \`data-step-active="true"\`

7. **Embedded Styling (REQUIRED):**
   - Include \`<style>\` tag with all CSS (see EXAMPLE ANIMATION STRUCTURE above)
   - Define all @keyframes animations
   - Ensure transitions work smoothly with 0.4s timing

8. **Responsiveness:**
   - Use \`viewBox="0 0 800 450"\` for consistent aspect ratio
   - Use relative sizing in SVG (no fixed pixel dimensions)
   - All text should scale with viewBox

9. **Self-Contained:**
   - All CSS and animations embedded in SVG
   - No external dependencies or HTTP requests
   - Should work as a standalone file

**Metadata Requirements:**

Generate metadata with:
- \`conceptName\`: The concept being explained (same as input)
- \`totalDuration\`: Total milliseconds for full simulation (sum of all step durations)
- \`fps\`: Target 30 FPS (optional)

**Output Structure:**

Your JSON response MUST include:
- \`diagramData.svgContent\`: Complete SVG with embedded styles
- \`diagramData.explanation\`: Top-level concept explanation
- \`diagramData.components\`: Array of component metadata (required)
- \`diagramData.steps\`: Array of step definitions with component references (required)
- \`diagramData.metadata\`: Diagram metadata

**Data Consistency Requirements (CRITICAL):**

Before returning your final JSON, verify:
1. Every component ID in \`steps[].activeComponentIds\` exists in \`components[]\` array
2. Every component ID in \`components[]\` has a matching SVG element in the diagram
3. No duplicate component IDs or step IDs
4. All required fields are populated (no null/empty values except optional fields)
5. Animation timing is always between 100-5000ms

If you find any inconsistencies, FIX THEM before returning the JSON.

**QUALITY STANDARDS (Non-negotiable):**

🔴 **CRITICAL - ANIMATIONS MUST CREATE VISUAL MOVEMENT:**
- Components MUST MOVE between positions (using CSS transform animations)
- Data/messages MUST FLOW between components (using animated stroke-dasharray)
- State transformations MUST be visually distinct (opacity, filter, and animation changes)
- **STATIC DIAGRAMS ARE NOT ACCEPTABLE** - if clicking "Start Simulation" doesn't show movement, it's wrong
- Every step should have at least one visual change or animation

- **Animation Quality:**
  - Use \`@keyframes\` for movement animations (moveLeft, moveRight, moveUp, moveDown)
  - Use \`stroke-dasharray\` animations for flowing arrows/connections
  - Use \`transform: translate()\` for smooth position changes
  - Use \`filter: brightness()\` and \`opacity\` for state changes
  - Timing: 1.2s total transition speed, 0.4s for attribute changes, 2s for continuous animations

- **Color Palette:** Use distinct, accessible colors (high contrast for readability)
- **Component Labels:** Keep labels short and clear
- **Step Descriptions:** Explain what happens and why at each step (these descriptions should match the visual animations)
- **Accuracy:** Ensure the diagram correctly represents how the system actually works
- **Data Integrity:** Ensure all referenced component IDs exist (no orphaned references)
- **Visual Hierarchy:** Components in focus should be bright/highlighted, inactive components faded

**CRITICAL ENHANCEMENT: Data Flow Visualization**

For each step, explicitly model data flows:
1. What data flows? (e.g., "HTTP request with headers and body")
2. From which component to which?
3. What transformation happens? (e.g., "Request is parsed")

Generate dataFlows array:
\`\`\`json
"dataFlows": [
  {
    "fromComponent": "client",
    "toComponent": "load-balancer",
    "dataType": "HTTP Request",
    "transformation": "Parsed and routed",
    "isRequired": true
  }
]
\`\`\`

**CRITICAL ENHANCEMENT: Debugging Metadata**

For EACH component, generate:
1. detailedExplanation: 2-3 sentences explaining HOW it works
2. inputs: List of inputs and meanings
3. outputs: List of outputs
4. failureMode: What happens if this component fails
5. failureRecovery: How the system recovers

Example:
\`\`\`json
"components": [
  {
    ...existing fields...,
    "detailedExplanation": "The load balancer uses Round-Robin algorithm to distribute requests across servers. It maintains a queue and assigns each to the next available server in rotation.",
    "inputs": ["HTTP request from client", "Server health status updates"],
    "outputs": ["Routed HTTP request to selected server"],
    "failureMode": "If load balancer fails, all client requests are dropped.",
    "failureRecovery": "Health check detects failure within 3 seconds. DNS switches traffic to backup load balancer."
  }
]
\`\`\`

**CRITICAL ENHANCEMENT: Real-World Domain Examples**

For EACH component, provide 2-5 real-world implementations:
\`\`\`json
"realWorldExamples": [
  {
    "technology": "AWS",
    "name": "Elastic Load Balancer (ELB)",
    "link": "https://docs.aws.amazon.com/elasticloadbalancing/"
  },
  {
    "technology": "Kubernetes",
    "name": "Ingress Controller (Nginx)",
    "link": "https://kubernetes.io/docs/concepts/services-networking/ingress/"
  }
]
\`\`\`

Also assign each component a layer: "core" (essential) or "advanced" (optional details).

**CRITICAL ENHANCEMENT: Scenarios**

Generate 3-5 "what if?" scenarios that test understanding:
\`\`\`json
"scenarios": [
  {
    "scenarioName": "High Traffic Load",
    "description": "Traffic suddenly increases 10x normal volume",
    "impactedComponents": ["load-balancer", "server-pool"],
    "visualization": {
      "highlightComponents": ["load-balancer"],
      "dimComponents": [],
      "animationType": "overload"
    },
    "lessonLearned": "Load balancer has limits; you need auto-scaling when traffic exceeds capacity."
  }
]
\`\`\`

Animation types: "overload", "failure", "slow", "bottleneck"

**CRITICAL ENHANCEMENT: Time Estimates & Prerequisites**

Estimate realistic learning time:
\`\`\`json
"timeEstimates": {
  "quickView": 3,
  "deepUnderstanding": 12,
  "masteryChallenges": 25
},
"conceptDifficulty": 6,
"prerequisites": ["Basic networking", "Understanding of HTTP"],
"keyInsights": [
  "Load balancing distributes traffic across multiple servers",
  "Health checks ensure traffic only goes to healthy servers",
  "Bottlenecks shift as you scale"
]
\`\`\`

**QUALITY ASSURANCE**

Before returning, verify:
1. Every component ID in steps exists in components array ✓
2. Every data flow references existing components ✓
3. Failure modes are realistic and non-contradictory ✓
4. Real-world examples are accurate (no hallucinated products) ✓
5. Scenarios are coherent with diagram structure ✓
6. Time estimates are reasonable (min 2 min, max 60 min) ✓

Self-score quality 0-100:
- 90-100: High confidence, accurate, well-structured
- 70-89: Good quality, minor issues
- Below 70: Concerns about accuracy or completeness

Return qualityScore and generationNotes in metadata.

**ANIMATION CHECKLIST (Must verify before returning):**
✓ Components move to different zones/positions in steps (using data-position or direct transforms)
✓ Arrows/connections have flowing animations (stroke-dasharray pattern)
✓ State transformations are animated (plaintext→encrypted, etc.)
✓ Hover effects show pulsing and highlighting
✓ Each step has distinct visual feedback
✓ Animations are smooth (use ease-in-out timing)
✓ Animations have purpose (not gratuitous, aligned with concept explanation)
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
