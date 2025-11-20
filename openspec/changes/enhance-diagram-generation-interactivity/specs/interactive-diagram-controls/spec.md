# Capability: Interactive Diagram Controls

## Overview

Provide users with interactive controls to explore, debug, and manipulate diagrams after rendering. Enable personalized learning through inspector panels, scenario testing, complexity toggling, and timeline navigation.

## ADDED Requirements

### Requirement: Component Inspector Panel
The system SHALL provide a clickable component inspector panel showing multi-layer metadata (overview, how it works, real-world examples, failure modes) when users click diagram components.

#### Scenario: Deep Dive on Component
User clicks "Load Balancer" component in diagram. Right-side panel slides in showing:
- **Overview tab**: Name, category, brief description
- **How It Works tab**: Detailed explanation with algorithm/logic
- **Real-World tab**: AWS ELB, Kubernetes Ingress, Nginx HAProxy with links
- **Failure Modes tab**: What happens if it fails, recovery mechanism
- **Inputs/Outputs**: What it receives and produces

Each tab has clear, readable text. Component is visually highlighted in diagram.

#### Specification
- Component in SVG has click listener (attached by frontend)
- On click, `onComponentSelected` callback fires with component ID
- Inspector panel renders with `ComponentInspectorPanel` React component
- Panel structure:
  ```typescript
  ComponentInspectorPanel {
    selectedComponent: Component
    onClose: () => void
  }
  ```
- Tabs implemented with Radix UI Tabs component
- Content populated from component metadata:
  - Overview: `label`, `description`, `category`
  - How It Works: `detailedExplanation`, `metrics` (throughput, latency)
  - Real-World: `realWorldExamples` array with clickable links
  - Failure Modes: `failureMode`, `failureRecovery`
  - Inputs/Outputs: `inputs`, `outputs` arrays
- Styling:
  - Slide-in animation from right (0.3s)
  - Max width 350px on desktop
  - Scrollable content if too long
  - Close button (X) in top right
  - Mobile: Switch to bottom sheet overlay
- On component hover (without click), show tooltip with brief description
- Click on real-world example link opens documentation in new tab

### Requirement: Scenario Testing UI
The system SHALL provide scenario testing buttons allowing users to simulate "what if?" conditions (failures, overload, slowness) and see diagram behavior changes.

#### Scenario: Testing System Under Stress
User sees button panel below diagram: "Test Scenarios"
- "High Traffic Load" - What if traffic 10x normal?
- "Server Failure" - What if one server crashes?
- "Network Slowdown" - What if connection is slow?
- "Cascading Failure" - What if multiple components fail?

User clicks "Server Failure". Diagram animates:
- Failed server grays out (opacity 0.3)
- Health check component highlights (green glow)
- Load balancer highlights (redirecting traffic)
- Animation shows requests rerouting to healthy servers
- Explanation appears: "Health check detects failure within 3 seconds. Load balancer automatically routes new requests to remaining servers."

#### Specification
- Scenario tester component `ScenarioTesterUI`:
  ```typescript
  ScenarioTesterUI {
    scenarios: Scenario[]
    activeScenario: string | null
    onScenarioSelect: (name: string) => void
  }
  ```
- Renders buttons for each scenario in list
- On click, scenario becomes active
- Visual feedback: Selected button has highlight
- Diagram updates to show scenario effect:
  - Apply CSS classes to SVG elements
  - Update animation based on scenario type:
    - "overload": Red glow, shake animation, slow down animation
    - "failure": Gray out, reduce opacity to 0.3
    - "slow": Keep same visuals but slow animation 2x
    - "bottleneck": Highlight connections, show queue building
- Scenario can be reset/deselected
- Scenario info (description, lesson learned) displays when active

### Requirement: Complexity Toggle (Frontend-Only)
The system SHALL provide instant CSS-based toggle to show/hide advanced components without regeneration or API calls.

#### Scenario: Adapting to Skill Level
User views "Load Balancer" beginner mode (default):
- Sees only 5 essential components: Client, Load Balancer, Server Pool, Health Check, Response
- Simple animation with basic data flow
- ~4 main steps

User clicks "Show Advanced Components". Instantly:
- Advanced components appear: Cache, Session State, Backup LB, Retry Logic, etc.
- All animations still work
- Additional steps show edge cases and optimization
- NO re-generation, NO API call, NO delay

User toggles OFF. Advanced components disappear again instantly.

#### Specification
- Toggle button component `ComplexityToggle`:
  ```typescript
  ComplexityToggle {
    showAdvanced: boolean
    onToggle: () => void
  }
  ```
- Toggle rendered in diagram header or control panel
- On click, toggle state and add/remove CSS class from SVG container
- CSS rule in SVG or stylesheet:
  ```css
  [data-layer="advanced"] {
    display: none;  /* Hidden by default */
  }

  body.show-advanced [data-layer="advanced"] {
    display: block;  /* Visible when toggled */
  }
  ```
  OR:
  ```css
  svg.show-advanced [data-layer="advanced"] {
    display: block;
  }
  ```
- Preference saved to localStorage:
  ```javascript
  localStorage.setItem('diagramShowAdvanced', showAdvanced ? 'true' : 'false')
  ```
- On next session with same concept, restore preference
- No content change, pure CSS display:none/block (instant, no re-render)
- Works with all diagram types
- Mobile: Toggle can be switch or button

### Requirement: Timeline Control (Scrubber)
The system SHALL provide a visual timeline with scrubber allowing users to jump to any step and see timeline labels on hover.

#### Scenario: Jumping to Specific Step
User sees visual timeline below diagram:
```
[Step 1: Request] [Step 2: Route] [Step 3: Process] [Step 4: Response]
  ◯━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ↑ Current position
```

User drags scrubber to "Step 3: Process". Diagram instantly jumps to that step.
User clicks "Step 1: Request" label. Diagram jumps there.

#### Specification
- Timeline component `TimelineControl`:
  ```typescript
  TimelineControl {
    steps: Step[]
    currentStep: number
    totalDuration: number
    onStepChange: (stepIndex: number) => void
  }
  ```
- Visual timeline shows:
  - Horizontal bar representing full animation duration
  - Scrubber/slider indicating current position
  - Step labels shown on hover or below timeline
  - Colors indicate step type or importance (optional)
- Interactions:
  - Click any point on timeline → jump to that step
  - Drag scrubber → scrub through steps
  - Keyboard: Arrow keys to move 1 step, Home/End to jump
- Current step highlighted with distinct style
- Mobile: Full-width timeline, touch-friendly scrubber
- Responsive: Adapts to container width

### Requirement: Enhanced Playback Controls
The system SHALL provide fine-grained playback controls including speed slider, previous/next/first/last buttons, and loop toggle.

#### Scenario: Controlling Animation Speed
User sees playback controls:
```
[|◀] [◀◀] [▶/⏸] [▶▶] [▶|]  Speed: [0.5x ←───●──→ 2x]  Loop: [On/Off]
```

User drags speed slider to 2x. Animation now plays twice as fast.
User clicks [◀◀] button. Steps back one step.
User clicks [|◀]. Jumps to first step.

#### Specification
- Enhanced controls in ControlPanel component
- New controls:
  - `|◀` (first): Jump to step 0
  - `◀◀` (previous): Decrement currentStep
  - `▶/⏸` (play/pause): Toggle isSimulating
  - `▶▶` (next): Increment currentStep
  - `▶|` (last): Jump to last step
  - Speed slider: 0.5x to 2x (default 1x)
  - Loop toggle: On/Off (default off)
- Speed control modifies animation interval:
  ```typescript
  const effectiveInterval = (2000 / playbackSpeed);
  setInterval(() => {
    setCurrentStep(prev => (prev + 1) % steps.length);
  }, effectiveInterval);
  ```
- Loop toggle:
  - ON: After last step, restart at step 0
  - OFF: Stop at last step
- Speed reflected in all animations (CSS and JS)
- Keyboard shortcuts (optional):
  - Space: Play/Pause
  - Arrow Left/Right: Previous/Next
  - Home/End: First/Last

### Requirement: Dependency Map Overlay
The system SHALL provide an optional dependency map overlay showing component connections with color-coded data flow paths.

#### Scenario: Understanding Data Flow Paths
User clicks "Show Dependencies". Overlay appears on diagram showing:
- Lines connecting components (green for input, blue for output)
- User clicks "Load Balancer" component
- All connections to/from it highlight in bright color
- Other connections fade (opacity 0.3)
- Labels show data type: "HTTP request", "Routed request"

User can trace path from Client → LB → Server visually.

#### Specification
- Dependency map component `DependencyMapOverlay`:
  ```typescript
  DependencyMapOverlay {
    connections: Connection[]
    selectedComponent?: string
    onComponentSelect: (id: string) => void
    visible: boolean
  }
  ```
- Rendered as SVG overlay on top of diagram
- Draws `<line>` or `<path>` elements for each connection
- Color coding:
  - Green: Input connections (arrow pointing in)
  - Blue: Output connections (arrow pointing out)
  - Red: Error/fallback connections (dashed)
- On component select, highlight its connections:
  - Selected component connections: opacity 1, bold
  - Other connections: opacity 0.3
- Tooltips show connection type: "HTTP Request", "Response", etc.
- Toggle button to show/hide overlay
- Mobile: Use diagram area carefully (may overlap if crowded)

### Requirement: Complexity Guidance
The system SHALL display clear metadata guidance showing component counts, difficulty ratings, and prerequisites to help users choose appropriate complexity level.

#### Scenario: User Choosing Appropriate Level
Toggle button shows labels:
- "Beginner (5-10 min)" - Green highlight, description: "Perfect for learning the basics"
- "Advanced" - Purple highlight, description: "Deep dive with edge cases"

Tooltip on hover shows:
- Component count
- Step count
- Difficulty rating (1-10)
- Prerequisite knowledge

#### Specification
- Complexity toggle includes metadata display:
  ```typescript
  ComplexityToggle {
    showAdvanced: boolean
    onToggle: () => void
    metadata?: {
      advancedComponentCount: number
      advancedStepCount: number
      difficultyRating: number
      prerequisitesAssumed: string[]
    }
  }
  ```
- Display shows:
  - Button label with time estimate
  - Hover tooltip with metadata
  - Difficulty indicator (stars, bar, or numeric)
- Responsive text that fits mobile screens

### Requirement: State Synchronization
The system SHALL coordinate all interactive controls (inspector, scenarios, complexity, timeline, playback) so they work together without conflicts.

#### Scenario: Using Multiple Controls Together
- User selects scenario (e.g., "Server Failure")
- Diagram highlights failed components
- User adjusts playback speed
- Scenario animation respects speed (slower/faster)
- User toggles complexity
- Advanced components appear/disappear, scenario updates
- User scrubs timeline
- Scenario resets (deselect scenario to continue)
- All features work together smoothly

#### Specification
- Controls are independent but coordinated:
  - Scenario and complexity: Scenario applies to current layer (core or advanced)
  - Timeline and scenario: Scrubbing deselects scenario (scenario is active state, not a step)
  - Speed and all: Affects all animations consistently
- No conflicting states (e.g., can't have two scenarios active)
- State management in parent component (page.tsx or parent of DiagramDisplay)
- State variables:
  - `currentStep`: number (0 to steps.length-1)
  - `isSimulating`: boolean (auto-play vs manual)
  - `playbackSpeed`: number (0.5 to 2)
  - `activeScenario`: string | null
  - `showAdvanced`: boolean
  - `selectedComponent`: string | null
- Clean state cleanup on unmount

## MODIFIED Requirements

### Requirement: DiagramDisplay Component (Enhanced)
DiagramDisplay SHALL be extended to support all interactive features (inspector, scenarios, complexity toggle, timeline) with new props and render logic.

#### Scenario: Enhanced Display with All Features
- User clicks component, inspector panel slides in from right
- User clicks scenario button, diagram animates with effects
- User toggles complexity, advanced components appear/disappear instantly
- User scrubs timeline, jumps to any step
- User adjusts speed, all animations update
- All features work together without conflicts

#### Specification
- Add props to DiagramDisplay:
  ```typescript
  interface DiagramDisplayProps {
    svgContent: string | null
    diagramData: DiagramContent | null
    isLoading: boolean
    currentStep: number
    isSimulating: boolean
    playbackSpeed: number
    activeScenario: string | null
    showAdvanced: boolean
    selectedComponent: string | null
    onComponentSelect: (id: string | null) => void
    onScenarioSelect: (name: string | null) => void
    onComplexityToggle: () => void
    onStepChange: (step: number) => void
    onSpeedChange: (speed: number) => void
  }
  ```
- Render new components:
  - ComponentInspectorPanel (conditional on selectedComponent)
  - ScenarioTesterUI (below SVG)
  - ComplexityToggle (in header)
  - TimelineControl (below SVG)
  - DependencyMapOverlay (optional, conditional)
  - PlaybackControls (in control panel or header)
- Handle SVG updates:
  - Add click listeners to components
  - Apply CSS classes for complexity toggle
  - Apply CSS filters for scenarios
  - Sync animations with playback speed

### Requirement: ControlPanel Component (Enhanced)
ControlPanel SHALL be extended with fine-grained playback controls (speed slider, previous/next/first/last buttons, loop toggle).

#### Scenario: Adding Playback Controls
- User drags speed slider from 0.5x to 2x, animation speed updates
- User clicks [|◀] to jump to first step
- User clicks [◀◀] to go to previous step
- User clicks [▶▶] to go to next step
- User clicks [▶|] to jump to last step
- User toggles loop, simulation restarts from beginning

#### Specification
- New controls in Simulation Mode section:
  - Speed slider (0.5x to 2x)
  - Button row: [|◀] [◀◀] [▶/⏸] [▶▶] [▶|]
  - Loop toggle
- Existing controls still work
- Mobile: Controls stack vertically or use drawer

## REMOVED Requirements

None. Pure addition to existing UI.

## Data Validation

### Inspector Panel Constraints
- All component metadata fields must be non-empty
- Links in real-world examples must be valid URLs
- Descriptions must be clear and concise

### Scenario Constraints
- Scenario name must be unique per diagram
- Impacted components must exist
- Animation type must be valid enum
- Lesson learned must be educational

### Timeline Constraints
- Step indices must be valid (0 to steps.length-1)
- Timeline must display all steps
- Scrubber must be draggable (mouse and touch)

### Playback Control Constraints
- Speed range: 0.5x to 2x
- Speed applied consistently to all animations
- Previous/next buttons respect step boundaries
- Loop works correctly (wraps to step 0)

## Cross-System Constraints

- Interactive controls don't modify diagram data (read-only)
- Scenario application is temporary (doesn't save)
- Complexity toggle uses CSS only (no SVG re-generation)
- Inspector panel doesn't block diagram interaction
- All controls work on mobile and desktop

## Performance Targets

- Component click response: <100ms
- Inspector panel slide-in animation: <300ms
- Scenario application: <50ms (CSS filter application)
- Complexity toggle: <16ms (instant, single CSS class add/remove)
- Timeline scrubbing: Smooth (no jank)
- All transitions use GPU-accelerated properties (transform, opacity)

## Accessibility Requirements

- All controls keyboard accessible (Tab, Arrow keys, Enter)
- Inspector panel has focus management (trap focus when open)
- Timeline scrubber has ARIA attributes
- Speed slider has ARIA value text
- Color not sole indicator (use icons, labels)
- Sufficient contrast (WCAG AA minimum)

## Success Criteria

1. **Inspector Usage**: 50%+ click at least one component
2. **Scenario Engagement**: 60%+ interact with scenario
3. **Complexity Adoption**: 40%+ toggle to advanced mode
4. **Timeline Usage**: 70%+ use timeline to navigate
5. **Control Satisfaction**: 4.5+/5 rating
6. **Performance**: No frame drops during interactions
7. **Accessibility**: Pass WCAG AA audit
8. **Mobile Experience**: 4.3+/5 on mobile devices

