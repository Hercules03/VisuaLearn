# Implementation Tasks

## 1. Genkit Flow Enhancement
- [x] 1.1 Update `src/ai/flows/generate-interactive-diagram.ts` output schema with DiagramContentSchema
  - [x] Add `components[]` array with component metadata structure
  - [x] Add `steps[].activeComponentIds` field
  - [x] Add `steps[].animationTiming` field (duration, easing)
  - [x] Add `metadata` object with totalDuration, fps
- [x] 1.2 Enhance Genkit prompt with component extraction examples
  - [x] Add example of well-structured component list
  - [x] Add example of step-to-component mapping
  - [x] Add animation timing specifications
  - [x] Add SVG element ID naming conventions
- [ ] 1.3 Create test fixtures for valid/invalid diagram schemas
  - [ ] Valid diagram with 3 components and 4 steps
  - [ ] Invalid diagram with missing component references
  - [ ] Invalid diagram with malformed SVG
- [x] 1.4 Update schema validation in `generateInteractiveDiagram` flow (integrated into lib/actions.ts)

## 2. Diagram Output Schema & Validation
- [x] 2.1 Define TypeScript interfaces for new diagram structure
  - [x] `DiagramComponent` interface (id, label, description, svgSelector, category)
  - [x] `DiagramStep` interface (id, title, description, activeComponentIds, animationTiming)
  - [x] `DiagramMetadata` interface (conceptName, totalDuration, fps)
  - [x] Enhanced `DiagramOutput` interface
- [x] 2.2 Create Zod validation schema for diagram output
  - [x] Component ID uniqueness validation
  - [x] SVG selector format validation
  - [x] Animation timing range validation (100-5000ms)
- [x] 2.3 Add validation utility function `validateDiagramSchema()`
  - [x] Check component ID consistency across steps
  - [x] Verify animation timing is realistic
  - [x] Report clear error messages for validation failures
  - [x] Created `src/lib/diagram-validation.ts` with comprehensive validation

## 3. Frontend: Diagram Display Component Enhancement
- [x] 3.1 Update `src/components/visualearn/diagram-display.tsx`
  - [x] Accept new diagram schema with components and metadata
  - [x] Render SVG with component interactivity
  - [x] Manage component highlighting state
  - [x] Handle hover/click events for component exploration
- [x] 3.2 Implement Component Explorer layer (The 'What')
  - [x] Hover event binding to SVG components
  - [x] Tooltip rendering on hover (bottom-left with component info)
  - [x] Component state attributes for CSS-based highlighting
  - [x] Component description display in tooltip
- [x] 3.3 Implement Step-by-Step Tutorial layer (The 'How')
  - [x] Track current step in component state (passed from parent)
  - [x] Apply active component highlighting based on step
  - [x] Support data attributes for CSS animation states
  - [x] Synchronize visual state with step changes
- [ ] 3.4 Implement Full Simulation Mode layer (The 'Review')
  - [ ] Create simulation loop with timing control
  - [ ] Auto-advance through steps at 2-3 second intervals
  - [ ] Loop back to step 1 seamlessly
  - [ ] Dynamic component highlighting during simulation
  - [ ] Pause/resume functionality

## 4. Frontend: Control Panel Enhancement
- [x] 4.1 Update `src/components/visualearn/control-panel.tsx`
  - [x] Add "Previous Step" and "Next Step" buttons (already existed, updated)
  - [x] Add "Start/Stop Simulation" toggle button (already existed, updated)
  - [x] Display current step counter (e.g., "Step 2 of 5")
  - [x] Disable navigation buttons at boundaries (step 1 prev, final step next)
- [x] 4.2 Pass control state to DiagramDisplay
  - [x] Bind button clicks to diagram step navigation
  - [x] Bind simulation toggle to auto-play mode
  - [x] Maintain synchronized step position across all interaction modes
- [x] 4.3 Updated step display to use new DiagramStep structure
  - [x] Display step title from `step.title`
  - [x] Display step description from `step.description`
  - [x] Show overview explanation from `diagramData.explanation`

## 5. D3.js Integration & Interactivity
- [ ] 5.1 Minify D3.js library for embedding (~30KB minified)
  - [ ] Source minified D3.js
  - [ ] Create build script to inline D3 in SVG generation
  - [ ] Test file size impact on diagram generation
  - **NOTE**: Current phase uses data attributes and CSS for highlighting; D3 embedding is optional for future enhancement
- [x] 5.2 Implement interactivity layer (Foundation)
  - [x] Event listeners for hover on SVG components
  - [x] State tracking for hovered/active components
  - [x] Visual attribute management via data attributes
  - [x] Support for CSS-based styling and animations
- [x] 5.3 Implement visual state transitions
  - [x] Data attribute based highlighting for step changes
  - [x] Support for component active states during steps
  - [x] Props passed for simulation state
  - [x] CSS framework ready for animations (data-step-active, data-component-hover)
- [ ] 5.4 Implement flow visualization
  - [ ] Animated arrows or gradients showing direction/flow
  - [ ] Dynamic highlighting for active elements during simulation
  - [ ] Color-coded categories (input, output, control, etc.)
  - **NOTE**: Will be implemented by Genkit in SVG with CSS animations based on data attributes

## 6. Error Handling & Validation
- [x] 6.1 Implement diagram schema validation
  - [x] Validate component ID consistency across steps
  - [x] Check component uniqueness
  - [x] Verify animation timing ranges (100-5000ms)
  - [x] Created `src/lib/diagram-validation.ts` with comprehensive validation
- [x] 6.2 Create error handling for invalid diagrams
  - [x] User-facing error messages via return values (no fallback data)
  - [x] Integrated into `src/lib/actions.ts`
  - [x] Preserve concept in state for retry
  - [x] Show error via toast in main app
- [x] 6.3 Handle missing/broken SVG content
  - [x] Detect empty/missing SVG content
  - [x] Validate SVG format (check for '<svg' tag)
  - [x] Provide actionable error messages
  - [x] No fallback values used per project constraints

## 7. Responsive Design & Accessibility
- [x] 7.1 Ensure responsive diagram scaling
  - [x] SVG uses 100% width/height with max-width
  - [x] Container is flex with responsive layout
  - [x] Tooltips positioned in absolute div (bottom-left)
  - [x] Uses Tailwind responsive classes (sm:, lg:, md:)
- [ ] 7.2 Implement keyboard navigation
  - [ ] Arrow keys to navigate steps (← previous, → next)
  - [ ] Space or Enter to toggle simulation
  - [ ] Tab navigation to controls
  - **NOTE**: Navigation buttons support tabbing; keyboard shortcuts can be added in future enhancement
- [x] 7.3 Add accessibility attributes
  - [x] Added `title` attributes to navigation buttons
  - [x] Used `sr-only` for screen reader text
  - [x] Component selection uses event listeners (accessible)

## 8. Testing & Quality Assurance
- [ ] 8.1 Test diagram generation with Genkit flow
  - [ ] Test with 5 different complex concepts
  - [ ] Verify component metadata accuracy
  - [ ] Verify step sequencing correctness
  - [ ] Verify SVG validity and embedding
  - **BLOCKED**: Requires Genkit API key and testing environment setup
- [ ] 8.2 Test component explorer layer
  - [ ] Hover effects work on all components
  - [ ] Tooltips appear at correct positions
  - [ ] Related component highlighting works
  - [ ] Mobile/click behavior works
- [ ] 8.3 Test step-by-step layer
  - [ ] Next/Previous buttons navigate correctly
  - [ ] Visual state updates with step changes
  - [ ] Text descriptions sync with visuals
  - [ ] Boundary conditions (first/last step) work
- [ ] 8.4 Test simulation mode
  - [ ] Auto-play advances at correct intervals (2-3 sec)
  - [ ] Seamless looping back to step 1
  - [ ] Pause/resume functionality works
  - [ ] Dynamic highlighting during simulation
  - **NOTE**: Simulation timing is handled by existing code in page.tsx
- [ ] 8.5 Test error handling
  - [ ] Invalid diagram schema shows error toast
  - [ ] Malformed SVG shows error toast
  - [ ] Validation prevents partial rendering
  - [ ] No fallback data used
- [ ] 8.6 Performance testing
  - [ ] SVG renders quickly
  - [ ] Event listeners don't cause memory leaks
  - [ ] Tooltips appear without lag

## 9. Documentation & Code Quality
- [x] 9.1 Code documentation
  - [x] Comprehensive JSDoc comments in validation functions
  - [x] Detailed prompt in Genkit flow explaining all requirements
  - [x] Component prop documentation
- [x] 9.2 TypeScript types and interfaces
  - [x] Exported all diagram types from generate-interactive-diagram.ts
  - [x] Strong typing throughout new code
  - [x] JSDoc for complex validation logic
- [ ] 9.3 Run linting and type checks
  - [ ] `npm run typecheck` - can be run after implementation testing
  - [ ] `npm run lint` - can be configured and run
- [ ] 9.4 Code review checklist
  - [x] All new code follows project conventions (use client, 'use server')
  - [x] No fallback data or default values (only errors via toast)
  - [x] Error handling via explicit return values
  - [x] Responsive design with Tailwind classes

## 10. Integration & Deployment
- [x] 10.1 Breaking change documentation
  - [x] Documented in proposal.md
  - [x] Error validation prevents old formats
  - [x] Migration path: regenerate diagrams
- [ ] 10.2 End-to-end testing
  - [ ] User submits concept
  - [ ] Diagram generates with new schema
  - [ ] All interaction modes work together
  - [ ] Responsive on desktop, tablet, mobile
  - **BLOCKED**: Requires environment with Genkit API key
- [ ] 10.3 Performance optimization
  - [ ] Profile actual event listener performance
  - [ ] Optimize SVG selector queries if needed
  - [ ] Minimize re-renders in React components
- [ ] 10.4 Deployment preparation
  - [ ] Genkit API key configuration
  - [ ] Monitor for validation errors in production
  - [ ] Prepare user communication about breaking change
