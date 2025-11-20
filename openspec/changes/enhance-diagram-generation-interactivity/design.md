# Design Document: Enhanced Diagram Generation & Interactivity

## Architecture Overview

### Current Flow
```
User Input (concept string)
    ↓
Genkit Prompt → AI generates diagram
    ↓
Parse output → DiagramContent
    ↓
Render SVG + steps + components
    ↓
User navigates with prev/next buttons
```

### Enhanced Flow
```
User Input (concept string)
    ↓
Genkit Prompt → AI generates:
  - SVG with data flow visualization
  - Component metadata (what/why/how/pitfalls)
  - Step state snapshots (component states, data transitions)
  - Real-world domain examples
  - Failure scenarios
  - Time estimates, prerequisites, insights
  - Self-quality score
    ↓
Parse output → Enhanced DiagramContent
    ↓
Frontend Rendering:
  ├─ Render SVG + step navigation
  ├─ Parse metadata → build interactive UX
  └─ Instantiate controls:
      ├─ Component Inspector (right panel)
      ├─ Scenario Buttons (bottom)
      ├─ Complexity Toggle (top)
      ├─ Timeline Scrubber
      ├─ Dependency Map (overlay)
      └─ Playback Controls
    ↓
User interaction:
  - Click component → Inspector shows details
  - Click scenario → SVG animates with changes
  - Toggle complexity → CSS hides/shows components (instant!)
  - Scrub timeline → Jump to any step
  - Adjust speed → Control animation flow
    ↓
Learn deeply & understand "why"
```

## Data Structure Enhancements

### Enhanced Component Structure

```typescript
Component {
  // Existing fields
  id: string                    // kebab-case unique ID
  label: string                 // Display name
  description: string           // 1-2 sentence description
  svgSelector: string           // CSS selector to target element
  category: string              // "control" | "input" | "output" | "process" | "sensor"

  // NEW: Debugging layers
  detailedExplanation: string   // 2-3 sentence deep explanation
  inputs: string[]              // e.g., ["HTTP request", "Server status"]
  outputs: string[]             // e.g., ["Routed request to server"]
  failureMode?: string          // What happens if this fails
  failureRecovery?: string      // How system recovers

  // NEW: Real-world examples
  realWorldExamples: {
    technology: string          // "AWS", "Kubernetes", "Nginx"
    name: string                // "Elastic Load Balancer", "Ingress Controller"
    link?: string               // Documentation link
  }[]

  // NEW: Layer/complexity management
  layer: "core" | "advanced"    // For complexity toggle (CSS-based)

  // NEW: Metrics/performance
  metrics?: {
    throughput?: string         // "1000 req/s"
    latency?: string            // "10-50ms"
    criticality?: "essential" | "important" | "optional"
  }
}
```

### Enhanced Step Structure

```typescript
Step {
  // Existing fields
  id: string
  title: string
  description: string
  activeComponentIds: string[]
  animationTiming?: AnimationTiming

  // NEW: State snapshot (for debugger mode)
  stateSnapshot?: {
    componentId: string
    state: "idle" | "processing" | "complete" | "error"
    dataIn?: string             // "HTTP request with payload 1.5MB"
    dataOut?: string            // "Routed to Server-1"
    metrics?: {
      load?: number             // 0-100%
      latency?: number          // milliseconds
      errors?: number           // count
    }
  }[]

  // NEW: Data flow visualization
  dataFlows?: {
    fromComponent: string
    toComponent: string
    dataType: string            // "HTTP request", "Response"
    transformation?: string     // "Encrypted with key"
    isRequired: boolean         // Critical path?
  }[]
}
```

### Enhanced DiagramContent Structure

```typescript
DiagramContent {
  // Existing fields
  svgContent: string
  explanation: string
  components: EnhancedComponent[]
  steps: EnhancedStep[]
  metadata: DiagramMetadata

  // NEW: Learning guidance
  timeEstimates: {
    quickView: number           // Minutes to watch animations
    deepUnderstanding: number   // Minutes to read all details
    masteryChallenges: number   // Minutes to test knowledge
  }

  conceptDifficulty: number     // 1-10 scale
  prerequisites: string[]       // ["Basic programming", ...]
  keyInsights: string[]         // 3-5 key takeaways

  // NEW: Real-world scenarios
  scenarios: {
    scenarioName: string        // "High Traffic Load"
    description: string
    impactedComponents: string[]
    visualization: {
      highlightComponents: string[]
      dimComponents: string[]
      animationType: "overload" | "failure" | "slow" | "bottleneck"
    }
    lessonLearned: string       // What this teaches
  }[]

  // NEW: Comparable concepts
  comparableConcepts: {
    conceptName: string
    similarity: string
    differences: string
    whenToUseEach: string
  }[]

  // NEW: Connections/dependencies
  connections: {
    fromComponent: string
    toComponent: string
    connectionType: "data-flow" | "control-flow" | "feedback"
    label: string               // "HTTP Request"
    isRequired: boolean
  }[]

  // NEW: Quality metrics
  qualityScore: number          // 0-100, AI self-assessment
  generationNotes: string[]     // ["High confidence", "Complex system", ...]
}
```

## Enhanced SVG Requirements

### SVG Attributes for Interactivity

All SVG elements should include data attributes for frontend logic:

```xml
<svg>
  <g id="component-1"
      data-component-id="load-balancer"
      data-layer="core"
      data-category="control">
    <!-- Component visual -->
  </g>

  <!-- Data flow indicators -->
  <path id="flow-req-1"
        data-flow="true"
        data-from="client"
        data-to="load-balancer"
        d="M 100 100 L 300 100"/>

  <!-- Step grouping for timeline -->
  <g id="step-1-group" data-step="1">
    <!-- Step-specific elements -->
  </g>
</svg>
```

### Animation Coordination

```css
/* Staggered animations for visual flow */
@keyframes dataFlow1 {
  0% { stroke-dashoffset: 20; opacity: 1; }
  100% { stroke-dashoffset: 0; opacity: 0.7; }
}

@keyframes dataFlow2 {
  0% { transform: translateX(0); opacity: 0; }
  100% { transform: translateX(200px); opacity: 1; }
  50% { opacity: 1; }
}

[data-flow="true"] {
  animation: dataFlow1 2s linear 0.5s infinite;  /* 0.5s delay for coordination */
}

[data-transforming="true"] {
  animation: transformState 0.8s ease-in-out forwards;
}

/* Complexity toggle */
[data-layer="advanced"] {
  display: none;  /* Hidden by default */
}

body.show-advanced [data-layer="advanced"] {
  display: block;  /* Visible when user toggles */
}
```

## Component Architecture (Frontend)

### New Interactive Components

```typescript
// 1. ComponentInspectorPanel
// Props: selectedComponent, componentMetadata
// Shows: What/How/Why/RealWorld/FailureMode tabs
// Behavior: Slide-in from right, shows component details

// 2. ScenarioTesterUI
// Props: scenarios, onScenarioClick
// Shows: Buttons for each scenario
// Behavior: Applies CSS filters to SVG on click

// 3. ComplexityToggle
// Props: isAdvancedShown, onToggle
// Shows: "Show Advanced Components" toggle
// Behavior: Adds/removes CSS class on SVG container

// 4. TimelineControl
// Props: steps, currentStep, onStepChange
// Shows: Timeline scrubber with step labels
// Behavior: Click/drag to jump to any step

// 5. DependencyMapOverlay
// Props: connections, onComponentSelect
// Shows: Component graph with highlighted paths
// Behavior: Click component to highlight connections

// 6. PlaybackControls
// Props: speed, isPlaying, onSpeedChange, onPlayChange
// Shows: Speed slider, play/pause/prev/next buttons
// Behavior: Modify animation speed and step navigation
```

### Modified Existing Components

```typescript
// DiagramDisplay
// NEW props: showInspector, selectedComponent, scenarios
// NEW logic: Render inspector panel, scenario buttons below diagram
// NEW state: Manage complexity toggle, timeline position

// ControlPanel
// NEW buttons: "Complexity Toggle", "Debug Mode", "Test Scenario"
// NEW state: Track playback speed, debug mode active
// UNCHANGED: Step navigation still works
```

## Genkit Prompt Enhancement

### New Prompt Sections

```
CRITICAL ENHANCEMENT: Data Flow Visualization

For each step, explicitly model:
1. What data flows? (e.g., "HTTP request with headers and body")
2. From which component to which?
3. What transformation happens? (e.g., "Request is parsed")
4. How does it connect visually in SVG? (paths, arrows)

Generate dataFlows array showing exact connections:
"dataFlows": [
  {
    "fromComponent": "client",
    "toComponent": "load-balancer",
    "dataType": "HTTP Request",
    "transformation": "Parsed and routed",
    "isRequired": true
  }
]

Generate SVG with animated flowing elements showing data movement.
Use stroke-dasharray animations for flowing effect.
```

```
CRITICAL ENHANCEMENT: Debugging Metadata

For EACH component, generate:
1. detailedExplanation: 2-3 sentences explaining HOW it works (algorithm, logic)
2. inputs: List of inputs it receives and their meaning
3. outputs: List of outputs it produces
4. failureMode: What happens if this component fails or becomes slow
5. failureRecovery: How the system detects and recovers from failure

Example:
"components": [
  {
    "id": "load-balancer",
    ...existing fields...,
    "detailedExplanation": "The load balancer uses Round-Robin algorithm to distribute incoming requests across multiple backend servers. It maintains a queue of incoming requests and assigns each to the next available server in rotation.",
    "inputs": ["HTTP request from client", "Server health status updates"],
    "outputs": ["Routed HTTP request to selected server"],
    "failureMode": "If load balancer fails, all client requests are dropped and connection is lost.",
    "failureRecovery": "Health check detects failure within 3 seconds. DNS switches traffic to backup load balancer automatically."
  }
]
```

```
CRITICAL ENHANCEMENT: Real-World Domain Examples

For EACH component, provide 2-5 real-world implementations:
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

These help learners connect abstract concepts to actual products they'll use.
```

```
CRITICAL ENHANCEMENT: Scenarios

Generate 3-5 "what if?" scenarios that test understanding:
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
  },
  {
    "scenarioName": "Server Failure",
    "description": "One of the backend servers crashes",
    "impactedComponents": ["server-1"],
    "visualization": {
      "highlightComponents": ["health-check"],
      "dimComponents": ["server-1"],
      "animationType": "failure"
    },
    "lessonLearned": "Health checks detect failures and reroute traffic to healthy servers."
  }
]
```

```
CRITICAL ENHANCEMENT: Time Estimates

Estimate realistic learning time:
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
  "Bottlenecks shift as you scale (network → server → database)"
]
```

```
QUALITY ASSURANCE

Before returning diagram, verify:
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

Return qualityScore in metadata. If <70, suggest regeneration.

"qualityScore": 87,
"generationNotes": ["High confidence", "Complex system with good flow"]
```

## Performance Optimization

### Generation Phase
- No additional API calls (all in single Genkit prompt)
- Metadata generation adds ~1-2 seconds to total generation time
- Compression: Metadata is lean (mostly text, few IDs)

### Rendering Phase
- CSS-based complexity toggle: Instant (no re-render)
- Component inspector: DOM parsing only (no API call)
- Scenario buttons: Apply CSS filters to existing SVG
- Timeline scrubber: Simple step state update
- All interactions happen in browser (no network delay)

### Storage
- Enhanced metadata: +5-10KB per diagram (acceptable)
- Cached diagrams remain same size (metadata is lean text)

## Testing Strategy

### Unit Tests
- Metadata parsing and validation
- Component dependency resolution
- Complexity layer filtering logic
- State snapshot calculation

### Integration Tests
- Genkit prompt enhancement produces valid metadata
- Frontend correctly interprets all metadata fields
- Scenario application works with different diagram types
- Complexity toggle with all component types

### E2E Tests
- Full workflow: Generate → Inspect → Test scenarios → Toggle complexity
- Timeline scrubbing works with all steps
- Speed control affects animation properly
- All interactive controls work on mobile/tablet

### User Testing
- A/B test: Inspector panel placement (right vs. bottom)
- Scenario engagement: Do users interact? Do they learn from scenarios?
- Metadata clarity: Are descriptions helpful?

## Migration & Rollout

### Phase 1: Safe Rollout (Week 4)
- Deploy generation enhancements to backend
- Add metadata to diagram output
- Frontend gracefully handles missing metadata (backward compatible)
- Test with 10 internal users

### Phase 2: Interactive Controls (Week 5)
- Deploy component inspector (non-intrusive, opt-in)
- Deploy scenario buttons (non-intrusive)
- Deploy complexity toggle (CSS-based, no risk)
- Test with 50 beta users

### Phase 3: Full Launch (Week 6)
- All features enabled by default
- Monitor quality metrics and user feedback
- Iterate based on usage patterns

## Success Criteria (Detailed)

| Feature | Criterion | Measurement |
|---------|-----------|-------------|
| Data Flow Clarity | 80%+ rate diagrams easy to follow | Survey + engagement |
| Inspector Usage | 50%+ click at least one component | Event tracking |
| Scenario Usage | 60%+ interact with at least one scenario | Event tracking |
| Complexity Toggle | 40%+ toggle to advanced mode | Event tracking |
| Quality Score | Average 75+/100 | Metadata analysis |
| Time Estimates | Accuracy within 20% | Actual vs. estimated |
| Performance | No slowdown vs. current | Monitoring |
| User Satisfaction | 4.3+/5 rating | Survey |

