# Design: Three-Layer Diagram Interactivity

## Context

VisualEarn currently generates static SVG diagrams with step-by-step breakdowns. Users have limited ways to explore content beyond sequential stepping. Educational research indicates that learners benefit from:
1. **Component-level exploration** (understand individual parts)
2. **Sequential understanding** (comprehend process flow)
3. **Holistic visualization** (see complete working system)

This change adds interactive capabilities to serve all three learning modalities.

## Goals

- Enable users to explore diagrams at three distinct interaction levels
- Support smooth animations without external dependencies (self-contained SVGs)
- Maintain responsive design across device sizes
- Provide Genkit with clear structured output requirements
- Keep implementation maintainable and testable

## Non-Goals

- Real-time collaborative editing or multi-user features
- Export/sharing functionality (separate future change)
- Mobile touch gestures (hover/click interfaces only)
- Multiple diagram formats beyond SVG

## Decisions

### Decision 1: SVG + D3.js Architecture
**What**: Diagrams use SVG with embedded D3.js (no external CDN dependencies) for interactivity and animation.

**Why**:
- D3.js provides powerful DOM manipulation and animation APIs
- Embedding D3 in SVG allows standalone, self-contained diagrams
- D3 handles complex animations more reliably than pure CSS
- Compatible with existing React component structure

**Alternatives Considered**:
- Pure CSS animations: Limited for complex state management and multi-component coordination
- Canvas-based: Harder to add interactive elements (hover, click, tooltips)
- GSAP library: Requires additional dependency; D3 is more suitable for data-driven animations

### Decision 2: Three-Layer UI Control Model
**What**: ControlPanel and DiagramDisplay coordinate three interaction modes: Explorer (What), Tutorial (How), Simulator (Review).

**Why**:
- Clear separation of concerns for each interaction style
- Users understand which mode they're in
- Genkit prompt can be specific about what each layer requires

**Alternatives Considered**:
- Single unified interface: Confusing which controls apply
- Nested modals: Slower interactions, more UI complexity

### Decision 3: Structured SVG Output Schema
**What**: Genkit generates JSON with explicit structure: `components[]`, `steps[]`, `animations[]`, `metadata`

**Why**:
- Enables reliable D3 data binding
- Clear contract between AI and frontend
- Supports validation and error handling
- Allows future enhancement without breaking changes

**Component Structure**:
```json
{
  "components": [
    {
      "id": "valve-a",
      "label": "Main Valve",
      "description": "Controls flow rate",
      "svgSelector": "#valve-a-path",
      "category": "control"
    }
  ],
  "steps": [
    {
      "id": "step-1",
      "title": "Initial State",
      "description": "System starts at rest",
      "activeComponentIds": ["valve-a"],
      "animationSequence": [...]
    }
  ]
}
```

### Decision 4: Embedded Dependency Strategy
**What**: D3.js included inline in generated SVG; no external HTTP requests.

**Why**:
- Users can run diagrams offline
- No dependency on CDN availability
- Self-contained deliverable for sharing/export (future)
- Aligns with existing project constraint

**Tradeoff**: Larger SVG file size (~50-100KB for D3 + diagram). Acceptable for educational use case.

### Decision 5: Animation State Management
**What**: Animations driven by state machine: Explorer (hover), Tutorial (step index), Simulator (looping)

**Why**:
- Predictable behavior across browser contexts
- Easier to test and debug
- Smoother transitions between modes
- Clear user expectations

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Large SVG file size | Slower loading, bandwidth | Gzip compression, lazy rendering of non-visible components |
| D3.js complexity in Genkit | Hard to guarantee valid output | Detailed prompt examples, validation schema, test fixtures |
| Browser SVG rendering limits | Performance on low-end devices | Test on older browsers, optimize animation frame rates |
| Ambiguous Genkit output | Invalid diagram structure | Strict Zod schema validation, clear error messages to users |

## Migration Plan

### Breaking Change Impact
- Existing diagrams will not render with new interactive features
- Users will see error: "This diagram uses legacy format. Please generate a new diagram."

### User-Facing Approach
1. **Clear Error Messaging**: Toast notification with "Generate New" button
2. **Simple Recovery**: One-click regeneration with same concept
3. **No Data Loss**: Concept history preserved, just need new generation

### Implementation Phases
1. **Phase 1**: Update Genkit flow with new output schema and enhanced prompt
2. **Phase 2**: Implement Component Explorer layer (What) in diagram-display
3. **Phase 3**: Implement Step-by-Step Tutorial layer (How)
4. **Phase 4**: Implement Full Simulation Mode layer (Review)
5. **Phase 5**: Integration testing and performance optimization

## Open Questions

1. **D3.js File Size**: Should we minify D3 inline, or accept ~50KB overhead per diagram?
   - **Current Plan**: Minify inline to ~30KB

2. **Accessibility**: How to handle hover-based interactions for keyboard/screen reader users?
   - **Current Plan**: Add keyboard navigation (arrow keys) alongside hover, ARIA labels

3. **Animation Performance**: Target FPS for smooth animations on older devices?
   - **Current Plan**: 30 FPS acceptable, test on devices from 2-3 years ago

4. **Genkit Prompt Complexity**: Can we rely on Gemini to consistently generate valid component metadata?
   - **Current Plan**: Use structured few-shot examples in prompt, validate strictly

## Implementation Notes

### Genkit Prompt Enhancement
Update `src/ai/flows/generate-interactive-diagram.ts` prompt to include:
- Explicit component list with unique IDs and categories
- Step descriptions aligned to SVG paths
- Animation timing and keyframes specifications
- Example of well-structured output

### React Integration
- Use `useEffect` to mount D3 visualization into React-managed SVG container
- Manage D3 selections separately from React state to avoid conflicts
- Use `ref` for direct DOM access

### Validation & Error Handling
- Validate component IDs exist in SVG
- Validate step activeComponentIds reference valid components
- Validate animation selectors match SVG elements
- Raise errors via toast (per project constraints)
