# Specification: Interactive Diagrams

## ADDED Requirements

### Requirement: Component Exploration Layer (The 'What')
The system SHALL generate SVG diagrams with interactive component highlighting and hover tooltips that display component definitions and properties.

#### Scenario: User hovers over component
- **WHEN** user moves mouse over a labeled SVG component (e.g., valve, organ, circuit element)
- **THEN** that component is visually highlighted (color change, border emphasis, or glow effect)
- **AND** a floating tooltip appears near the cursor displaying the component's name and a concise 1-2 sentence definition
- **AND** related components in the same category are also subtly highlighted to show relationships

#### Scenario: Tooltip shows complete component metadata
- **WHEN** a user hovers over a component
- **THEN** the tooltip displays:
  - Component name (e.g., "Main Valve")
  - Category label (e.g., "control", "input", "output")
  - 1-2 sentence functional description
  - Optional: Input/output flow indicators

#### Scenario: Component explorer responds to mobile/touch
- **WHEN** user is on a tablet or lacks hover capability
- **THEN** clicking a component shows the tooltip persistently
- **AND** clicking elsewhere or another component dismisses the previous tooltip

---

### Requirement: Step-by-Step Tutorial Layer (The 'How')
The system SHALL enable users to navigate through logical process phases with animated SVG transitions and synchronized text descriptions.

#### Scenario: User steps through process manually
- **WHEN** user clicks "Next Step" or "Previous Step" button in ControlPanel
- **THEN** the diagram animates to highlight only the components active in that step
- **AND** inactive components fade or become translucent
- **AND** a text description area updates with a clear explanation of what is happening in the current step
- **AND** button state reflects navigation boundaries (disable "Previous" on step 1, disable "Next" on final step)

#### Scenario: Step animations are smooth and coordinated
- **WHEN** user navigates to a new step
- **THEN** transitions complete in 300-500ms with easing functions
- **AND** all component animations (fades, highlights, motion) synchronize seamlessly
- **AND** text description updates simultaneously with visual transition

#### Scenario: Step counter and progress are visible
- **WHEN** viewing a diagram with multiple steps
- **THEN** ControlPanel displays current step number and total step count (e.g., "Step 2 of 5")
- **AND** an optional progress indicator (bar, dots, or numbers) shows position in sequence

---

### Requirement: Full Simulation Mode (The 'Review')
The system SHALL provide a continuous auto-play simulation mode that loops through all diagram steps, demonstrating the complete workflow in real-time with dynamic component highlighting.

#### Scenario: User starts simulation
- **WHEN** user clicks "Start Simulation" toggle button
- **THEN** the diagram automatically advances through all steps in sequence
- **AND** each step displays for 2-3 seconds before advancing to the next
- **AND** transitions between steps animate smoothly
- **AND** button label changes to "Stop Simulation"

#### Scenario: Simulation loops continuously
- **WHEN** simulation reaches the final step
- **THEN** it loops back to step 1 seamlessly
- **AND** the cycle repeats until user clicks "Stop Simulation"
- **AND** no visual or audio indicators suggest restart (seamless loop)

#### Scenario: Dynamic flow highlighting during simulation
- **WHEN** simulation is running
- **THEN** active components are highlighted in real-time as the process flows
- **AND** if the concept involves energy/fluid/signal flow, animated arrows or gradients show direction
- **AND** components transition from "active" (bright color) to "inactive" (muted) as the process advances

#### Scenario: User can stop and resume simulation
- **WHEN** user clicks "Stop Simulation" while running
- **THEN** the diagram pauses on the current step
- **AND** the auto-advance timer stops
- **AND** user can then manually step forward/backward or restart simulation
- **AND** clicking "Start Simulation" again resumes from current step

#### Scenario: Simulation controls are disabled when irrelevant
- **WHEN** the diagram has only 1 step (no sequence)
- **THEN** simulation controls (Start/Stop, Next/Previous) are hidden or disabled
- **AND** user can still explore components with hover/tooltips

---

### Requirement: Diagram Output Schema
The system (Genkit) SHALL generate diagrams with a structured JSON schema that explicitly defines components, steps, animation sequences, and interactivity metadata.

#### Scenario: Genkit generates valid diagram schema
- **WHEN** AI processes a concept request
- **THEN** the returned diagram object includes:
  - `components[]` array with unique IDs, labels, descriptions, SVG selectors, and categories
  - `steps[]` array with step ID, title, description, active component IDs, and animation timing
  - `metadata` object with concept name, total duration, and animation frame rate
  - `svgContent` string with fully formed SVG including embedded D3.js and CSS
- **AND** all component IDs referenced in steps exist in the components array
- **AND** all SVG selectors in components array have matching elements in the generated SVG

#### Scenario: Diagram includes self-contained dependencies
- **WHEN** the diagram is generated
- **THEN** the SVG includes embedded:
  - D3.js library (minified, ~30KB)
  - All CSS for interactivity (hover states, animations, tooltips, highlights)
  - All JavaScript for state management and event handling
- **AND** no external CDN or HTTP requests are required to run the diagram
- **AND** the SVG can be saved to a file and opened directly in a browser

---

### Requirement: Interactive Diagram Display Component
The system SHALL render generated interactive diagrams with full support for all three interaction layers and responsive design.

#### Scenario: Diagram displays with all interaction layers available
- **WHEN** a diagram is generated and displayed in DiagramDisplay component
- **THEN** all three interaction layers are simultaneously available:
  - Component Exploration: hover any component to see tooltip
  - Step-by-Step: Previous/Next buttons navigate through steps
  - Simulation: Start/Stop button auto-plays sequence
- **AND** layers do not conflict or interfere with each other
- **AND** switching between layers maintains current step position

#### Scenario: Diagram is responsive on different screen sizes
- **WHEN** diagram is viewed on desktop, tablet, or small screen
- **THEN** the SVG scales proportionally without distortion
- **AND** tooltips reposition to remain visible (not cut off by viewport edges)
- **AND** control buttons remain accessible and properly sized
- **AND** text descriptions remain readable

#### Scenario: Diagram handles animation frame rates gracefully
- **WHEN** diagram animations are running
- **THEN** animations target 30 FPS minimum
- **AND** animations degrade gracefully on low-end devices (no frame drops stop interaction)
- **AND** users can always pause/resume simulation regardless of performance

---

### Requirement: Error Handling for Interactive Diagrams
The system SHALL detect and report errors in diagram structure with clear user-facing messages.

#### Scenario: Invalid component references are caught
- **WHEN** generated diagram has step that references non-existent component ID
- **THEN** the system validates schema during diagram load
- **AND** raises error via toast notification: "Diagram structure error: Component 'X' not found. Please regenerate."
- **AND** diagram does not render partially or incorrectly
- **AND** no fallback or default values are used (per project constraints)

#### Scenario: SVG rendering errors are reported
- **WHEN** generated SVG has invalid XML or missing selectors
- **THEN** validation catches the error before display
- **AND** user receives: "Failed to generate diagram. Please try again."
- **AND** user can click "Generate New" to retry
- **AND** original concept is preserved for retry

---

## MODIFIED Requirements

### Requirement: Generate Interactive Diagram Flow
The system SHALL generate interactive diagrams with complete components metadata, annotated steps, and embedded D3.js interactivity, replacing the previous simple SVG with steps approach.

**Previous Requirements**: The system generated SVG content and a flat steps array containing only text descriptions.

**Additions**: The system now SHALL also generate and return:
- Complete components array with metadata (IDs, definitions, categories, SVG selectors)
- Annotated steps with activeComponentIds arrays and animation timing specifications
- SVG with embedded D3.js library and interactive CSS
- Validation-friendly structured schema

**Prompt Enhancements**: The Genkit prompt SHALL be updated to:
- Provide explicit examples of component structure with IDs and categories
- Specify SVG element ID naming conventions
- Request animation timing specifications in step definitions
- Emphasize importance of component ID consistency across all steps

#### Scenario: Genkit generates diagram with all required fields
- **WHEN** user submits a concept for diagram generation
- **THEN** the returned `generateInteractiveDiagram` output includes all components, steps, metadata, and SVG as specified above
- **AND** the SVG content is a valid, standalone HTML/SVG file with embedded dependencies
- **AND** frontend validation confirms schema compliance before rendering

#### Scenario: Frontend validates Genkit output structure
- **WHEN** diagram output is received from Genkit
- **THEN** frontend MUST validate:
  - All referenced component IDs in steps exist in the components array
  - All step IDs are unique
  - SVG selectors match actual elements in the provided SVG
  - Animation timing values are realistic (100-5000ms range)
- **AND** validation errors MUST prevent rendering and display clear error messages via toast
