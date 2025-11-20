# Implementation Tasks: Enhanced Diagram Generation & Interactivity

## Phase 1: Enhanced Diagram Generation (Weeks 1-3)

### Week 1: Data Flow & Enhanced Metadata Structure

#### Task 1.1: Extend Component Schema
- [ ] Update `DiagramComponentSchema` in `generate-interactive-diagram.ts`
  - Add `detailedExplanation`, `inputs`, `outputs`, `failureMode`, `failureRecovery`
  - Add `realWorldExamples` array with technology/name/link
  - Add `layer` field ("core" | "advanced")
  - Add `metrics` object (throughput, latency, criticality)
- [ ] Update TypeScript interfaces to match schema
- [ ] Validate new fields don't break existing diagrams (backward compatibility)

#### Task 1.2: Extend Step Schema
- [ ] Update `DiagramStepSchema`
  - Add `stateSnapshot` array for component states
  - Add `dataFlows` array showing data movement
- [ ] Create `StateSnapshot` and `DataFlow` type definitions
- [ ] Document structure in code comments

#### Task 1.3: Extend DiagramContent Schema
- [ ] Update `DiagramContentSchema`
  - Add `timeEstimates`, `conceptDifficulty`, `prerequisites`, `keyInsights`
  - Add `scenarios` array with scenario definition
  - Add `comparableConcepts` array
  - Add `connections` array for dependency mapping
  - Add `qualityScore` and `generationNotes`
- [ ] Update `DiagramContent` TypeScript interface
- [ ] Test schema with sample data

#### Task 1.4: Enhance Genkit Prompt - Part 1: Data Flow
- [ ] Modify `generate-interactive-diagram.ts` prompt section
  - Add "DATA FLOW VISUALIZATION" instructions (from design doc)
  - Instruct AI to generate `dataFlows` array
  - Instruct AI to generate SVG elements with `data-flow` attributes
  - Instruct AI to use stroke-dasharray animations for flow visualization
- [ ] Test prompt with 3 sample concepts
- [ ] Verify AI generates `dataFlows` correctly

#### Task 1.5: Enhance Genkit Prompt - Part 2: Debugging Metadata
- [ ] Add "DEBUGGING METADATA" section to prompt
  - For each component: detailedExplanation, inputs, outputs, failureMode, failureRecovery
  - Provide examples in prompt
- [ ] Test with 3 sample concepts
- [ ] Verify quality of debugging explanations

### Week 2: Real-World Examples, Scenarios, Time Estimates

#### Task 2.1: Enhance Genkit Prompt - Part 3: Real-World Examples
- [ ] Add "REAL-WORLD DOMAIN EXAMPLES" section
  - Instruct AI to provide 2-5 real-world implementations per component
  - Include technology name and link
  - Emphasize accuracy (no hallucinated products)
- [ ] Test with 5 concepts across different domains
- [ ] Verify examples are accurate and helpful

#### Task 2.2: Enhance Genkit Prompt - Part 4: Scenarios
- [ ] Add "SCENARIO GENERATION" section
  - Instruct AI to generate 3-5 "what if?" scenarios
  - Define scenario structure: name, description, impactedComponents, visualization, lesson
  - Visualization types: "overload", "failure", "slow", "bottleneck"
  - Link scenarios back to concept learning
- [ ] Test with 3 concepts
- [ ] Verify scenarios are realistic and educational

#### Task 2.3: Enhance Genkit Prompt - Part 5: Time Estimates
- [ ] Add "TIME ESTIMATION" section
  - quickView: Time to watch animations only
  - deepUnderstanding: Time to read all explanations
  - masteryChallenges: Time to complete challenges
  - conceptDifficulty: 1-10 scale
  - prerequisites: List what users should know
  - keyInsights: 3-5 key takeaways
- [ ] Test estimates with actual user testing (Week 6)
- [ ] Validate estimates are accurate

#### Task 2.4: Enhance Genkit Prompt - Part 6: Comparable Concepts
- [ ] Add "COMPARABLE CONCEPTS" section
  - Instruct AI to identify 2-3 related concepts
  - Generate similarity/differences/whenToUseEach
  - Will be used in future for concept comparison feature
- [ ] Test with 3 concepts

#### Task 2.5: Enhance Genkit Prompt - Part 7: Quality Assurance
- [ ] Add "QUALITY ASSURANCE" section to prompt
  - Verification checklist (components exist, references valid, etc.)
  - Self-scoring (0-100)
  - Generation notes explaining confidence
- [ ] Instruct AI to validate before returning
- [ ] Test with 5 concepts, analyze quality scores

### Week 3: Validation, Testing, Refinement

#### Task 3.1: Extend Diagram Validation
- [ ] Update `validateDiagramSchema` in `diagram-validation.ts`
  - Validate all new metadata fields
  - Check data flow references valid components
  - Validate scenario structures
  - Check time estimates are reasonable (2-60 min)
  - Validate prerequisites array is non-empty
- [ ] Test with 10 generated diagrams
- [ ] Ensure backward compatibility (old diagrams without new fields still work)

#### Task 3.2: Create Metadata Utilities
- [ ] Create `src/lib/diagram-metadata.ts`
  - `extractComponentsByLayer(diagram, layer)` - filter by core/advanced
  - `getComponentDetails(diagram, componentId)` - return full component with debugging info
  - `getScenariosByType(diagram, type)` - filter scenarios
  - `calculateTotalLearningTime(diagram)` - sum time estimates
- [ ] Test utilities with sample diagrams
- [ ] Ensure performance is acceptable

#### Task 3.3: Comprehensive QA Testing
- [ ] Generate diagrams for 20 diverse concepts
  - Different domains: tech, biology, business, physics
  - Different complexity: simple, moderate, complex
- [ ] For each, verify:
  - All metadata fields are present
  - Data flows reference valid components
  - Real-world examples are accurate
  - Scenarios are coherent
  - Quality score is reasonable
  - Time estimates are plausible
- [ ] Document any issues and refinements needed
- [ ] Update prompt if needed to improve quality

#### Task 3.4: Performance Benchmarking
- [ ] Measure generation time with enhanced prompt
  - Compare to baseline (current prompt)
  - Target: <2 seconds additional time
- [ ] Measure output size (diagram + metadata)
  - Target: <50KB total
- [ ] Cache 10 diagrams, measure storage impact
- [ ] Optimize if needed (prompt compression, metadata pruning)

#### Task 3.5: Integration Testing
- [ ] Test enhanced generation with existing UI
  - Ensure backward compatibility
  - UI still renders without new metadata
- [ ] Test with diagram display component
  - Verify SVG renders correctly with new attributes
  - Data flow animations work
- [ ] Fix any issues found

---

## Phase 2: Post-Generation Interactive Controls (Weeks 4-5)

### Week 4: Component Inspector & Scenario Testing

#### Task 4.1: Build Component Inspector Panel Component
- [ ] Create `src/components/visualearn/component-inspector-panel.tsx`
  - Props: `selectedComponent: Component | null`, `onClose: () => void`
  - Render tabs: Overview | How It Works | Real-World | Failure Modes
  - Styled panel that slides in from right side
  - Mobile responsive (use bottom sheet on small screens)
- [ ] Implement tab switching with smooth transitions
- [ ] Style with Tailwind CSS, match existing design system
- [ ] Test with different component metadata

#### Task 4.2: Integrate Inspector with DiagramDisplay
- [ ] Update `DiagramDisplay` component
  - Add `selectedComponent` state
  - On component hover/click in SVG, set `selectedComponent`
  - Render `ComponentInspectorPanel` when component selected
  - Add click handler for SVG elements
- [ ] Test click detection with sample diagram
- [ ] Ensure hover tooltip still shows (or replace with inspector)

#### Task 4.3: Build Scenario Tester Component
- [ ] Create `src/components/visualearn/scenario-tester.tsx`
  - Props: `scenarios: Scenario[]`, `onScenarioSelect: (name) => void`
  - Render buttons for each scenario (or vertical list)
  - Show scenario description on hover
  - Icon indicators for scenario type (overload, failure, slow, etc.)
- [ ] Responsive layout (horizontal scroll on mobile)
- [ ] Styled consistently with existing components

#### Task 4.4: Integrate Scenario Application with SVG
- [ ] Update `DiagramDisplay` component
  - Track `activeScenario` state
  - On scenario select, apply CSS filters/classes to SVG
  - SVG animations reflect scenario:
    - Overload: Red glow, shake animation, increased opacity
    - Failure: Gray out components, reduce opacity
    - Slow: Slow down animation speed, increase latency indicators
    - Bottleneck: Highlight connection paths, show queue building
- [ ] Test each scenario type with sample diagram
- [ ] Ensure scenario resets when deselected

#### Task 4.5: Create Scenario CSS Animations
- [ ] Add to SVG styles (or separate stylesheet):
  - `.scenario-overload` - red glow, shake animation
  - `.scenario-failure` - opacity reduction, grayed out
  - `.scenario-slow` - delayed animations, progress bars
  - `.scenario-bottleneck` - highlight paths, queue animation
- [ ] Test animations work with existing diagram animations
- [ ] Ensure performance remains smooth

### Week 5: Complexity Toggle, Timeline, & Polish

#### Task 5.1: Implement Complexity Toggle (CSS-based)
- [ ] Update Genkit prompt (if needed) to ensure components have `layer` field
- [ ] Create `src/components/visualearn/complexity-toggle.tsx`
  - Props: `showAdvanced: boolean`, `onToggle: () => void`
  - Simple toggle button or switch
  - Show label: "Show Advanced Components"
- [ ] Update `DiagramDisplay` component
  - Add `showAdvanced` state
  - Add/remove CSS class on SVG container: `.show-advanced`
  - Save preference to localStorage
- [ ] Add CSS rules:
  ```css
  [data-layer="advanced"] { display: none; }
  .show-advanced [data-layer="advanced"] { display: block; }
  ```
- [ ] Test toggle works instantly (no re-render or API call)
- [ ] Test persistence (preference saved across sessions)

#### Task 5.2: Build Timeline Control Component
- [ ] Create `src/components/visualearn/timeline-control.tsx`
  - Props: `steps: Step[]`, `currentStep: number`, `onStepChange: (step) => void`
  - Visual timeline showing all steps
  - Scrubber/slider to move between steps
  - Labels for each step on hover
  - Click to jump to any step
- [ ] Make responsive (full width, adjust height)
- [ ] Add visual indicator for current position

#### Task 5.3: Integrate Timeline with Diagram Navigation
- [ ] Update `page.tsx` (or parent component)
  - Render `TimelineControl` below diagram
  - Connect `currentStep` state to timeline
  - On timeline change, update `currentStep`
  - Existing step navigation (prev/next buttons) still works
- [ ] Test timeline scrubbing works smoothly
- [ ] Test edge cases (jump to first/last step, rapid clicks)

#### Task 5.4: Enhance Playback Controls
- [ ] Update `ControlPanel` component
  - Add speed slider (0.5x to 2x)
  - Add previous/next buttons
  - Add play/pause toggle
  - Existing controls still work
- [ ] Modify simulation interval based on speed:
  ```typescript
  const interval = setInterval(
    () => setCurrentStep(prev => (prev + 1) % steps.length),
    (2000 / playbackSpeed)  // e.g., 2000ms / 2 = 1000ms for 2x speed
  );
  ```
- [ ] Test speed control works smoothly
- [ ] Test with all complexity levels

#### Task 5.5: Build Dependency Map Overlay (Optional - MVP)
- [ ] Create `src/components/visualearn/dependency-map.tsx`
  - Props: `connections: Connection[]`, `selectedComponent?: string`
  - Overlay on top of diagram
  - Show connections as colored lines
  - Highlight selected component's connections
  - Color code: Green (input), Blue (output), Red (error path)
- [ ] Add toggle button to show/hide dependency map
- [ ] Test with complex diagram

#### Task 5.6: Integration & Polish
- [ ] Test all interactive features together:
  - Click component → Inspector shows
  - Select scenario → SVG updates
  - Toggle complexity → Components hide/show
  - Scrub timeline → Jump to step
  - Change speed → Animation updates
- [ ] Fix any conflicts between features
- [ ] Ensure mobile experience is good
- [ ] Performance optimization pass (lazy load inspector, etc.)

---

## Phase 3: Testing & Launch (Week 6)

### Task 6.1: Comprehensive QA
- [ ] Generate diagrams for 15 diverse concepts
- [ ] Test all features with each diagram:
  - Component inspector shows correct metadata
  - Scenarios apply correctly
  - Complexity toggle works
  - Timeline scrubbing works
  - Playback controls work
  - No JavaScript errors
- [ ] Cross-browser testing (Chrome, Firefox, Safari, Edge)
- [ ] Mobile testing (iOS, Android)
- [ ] Document any bugs found

### Task 6.2: User Testing
- [ ] Recruit 10-15 beta testers
- [ ] Provide usage guide (brief)
- [ ] Collect feedback:
  - Which features are most useful?
  - Which controls are confusing?
  - Does learning improve with new features?
- [ ] Iterate based on feedback

### Task 6.3: Performance Optimization
- [ ] Measure generation time (target: <20s)
- [ ] Measure rendering time (target: <2s)
- [ ] Measure interaction latency (target: <100ms)
- [ ] Optimize any bottlenecks found
- [ ] Memory profiling (check for leaks)

### Task 6.4: Documentation & Launch Prep
- [ ] Update code comments
- [ ] Create user guide for new features
- [ ] Update project README with new capabilities
- [ ] Prepare launch announcement
- [ ] Set up monitoring for new metrics

### Task 6.5: Launch & Monitor
- [ ] Deploy to production
- [ ] Monitor error rates, performance metrics
- [ ] Collect user feedback
- [ ] Fix critical issues immediately
- [ ] Plan improvements based on usage

---

## Success Criteria Verification

By end of Phase 3, verify:

- [ ] Data flow visualization: 80%+ rate diagrams easy to follow
- [ ] Component inspector: 50%+ click at least one component
- [ ] Scenario testing: 60%+ interact with scenario
- [ ] Complexity toggle: 40%+ toggle to advanced mode
- [ ] Timeline: 70%+ use timeline to navigate
- [ ] Quality score: Average 75+/100
- [ ] Performance: Generation time <20s, render time <2s
- [ ] User satisfaction: 4.3+/5 rating
- [ ] No major bugs in testing

