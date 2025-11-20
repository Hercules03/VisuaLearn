# Project Context

## Purpose
VisualEarn is an interactive educational platform that generates animated SVG diagrams to explain complex concepts. Users input a topic, and the system leverages Google's Gemini AI via Genkit to create self-contained, interactive diagrams with step-by-step explanations and related concept suggestions. The goal is to make learning visual, interactive, and engaging.

## Tech Stack
- **Framework**: Next.js 15.3.3 (with Turbopack)
- **Language**: TypeScript 5 (strict mode)
- **Frontend**: React 18.3.1 (client-side with 'use client')
- **AI/ML**: Genkit 1.20.0 + Google Genkit (@genkit-ai/google-genai)
- **UI Components**: Radix UI (comprehensive component library)
- **Styling**: Tailwind CSS 3.4.1 with class-variance-authority
- **Forms**: React Hook Form 7.54.2 + Zod 3.24.2 (validation)
- **Data Visualization**: Recharts 2.15.1
- **Backend**: Firebase (v11.9.1)
- **Animation**: tailwindcss-animate
- **Icons**: Lucide React 0.475.0
- **Utilities**: date-fns, clsx, tailwind-merge

## Project Conventions

### Code Style
- **TypeScript**: Strict mode enabled (`"strict": true`), no implicit any
- **Path Aliases**: Use `@/*` for imports from `src/` directory (e.g., `@/components`, `@/lib`)
- **Component Structure**:
  - Use functional components with React Hooks
  - Prefer 'use client' for client-side interactivity
  - 'use server' for server-side flows (AI generation)
- **Naming**: PascalCase for components, camelCase for functions/variables, UPPER_CASE for constants
- **Formatting**: Next.js built-in linting (`next lint`), no external prettier config

### Architecture Patterns
- **Server Components with Client Islands**: Use Next.js server components by default, 'use client' only where needed
- **Genkit Flows**: AI operations defined in `src/ai/flows/` as separate modular functions
- **Component Organization**:
  - `src/components/ui/`: Reusable UI components (form inputs, dialogs, etc.)
  - `src/components/visualearn/`: Feature-specific components (control panel, diagram display, etc.)
  - `src/hooks/`: Custom React hooks (use-toast, use-mobile)
  - `src/lib/`: Utility functions, actions, and helpers
  - `src/ai/`: AI flow definitions and Genkit configuration

### Testing Strategy
- Currently: Manual testing through development
- Infrastructure: Genkit provides flow testing capabilities (via `genkit start`)
- Future: Consider unit tests for utility functions, integration tests for AI flows

### Git Workflow
- **Main Branch**: Primary development branch
- **Commit Conventions**: Follow conventional commits when possible
  - Format: `type(scope): description` (e.g., `feat(diagram): add animation controls`)
  - Types: feat, fix, docs, style, refactor, perf, test, chore
- **Code Review**: Changes reviewed before merge to main

## Domain Context

### Educational Technology
- Focus on visual learning and interactive explanations
- Each generated diagram must include:
  - SVG visual representation with embedded CSS
  - Textual explanation of the concept
  - Numbered steps for step-by-step learning
  - Interactive components (tooltips for "What", annotations for "Why", highlights for "How")

### AI Generation Pipeline
- **Input**: User-provided concept (string)
- **Processing**: Genkit flow using Gemini-3-Pro-Preview model
- **Output**: Structured object with SVG content, explanation, and steps array
- **Error Handling**: Errors should be communicated via toast notifications (no fallback data)

### User Interaction Flow
1. User submits a concept in ControlPanel
2. System triggers diagram generation via `handleGeneration` action
3. Results displayed in DiagramDisplay (SVG) and RelatedConcepts (clickable suggestions)
4. Users can manually step through or auto-simulate the diagram (2-second intervals)

## Important Constraints

### Data Handling
- **No Fallback Data**: All errors must be raised through toast notifications
- **No Default Values**: Raise errors explicitly rather than providing defaults
- **Strict Validation**: Use Zod schemas for all input validation
- **Legacy Code Removal**: Remove any fallback mechanisms and old conditional branches

### AI Model
- Currently using `gemini-3-pro-preview` (preview model)
- Genkit framework dependency (Google-provided)
- All AI operations are asynchronous server functions

### Performance
- Interactive diagram animations must be smooth (CSS-based, not frame-dependent)
- Step simulation uses 2-second intervals
- SVG generation should complete within reasonable timeout

### Browser Compatibility
- Mobile-first responsive design (Tailwind classes for breakpoints)
- SVG animations require CSS support
- React 18+ features available (Suspense, Transitions, etc.)

## External Dependencies

### Google Cloud / Firebase
- **Service**: Google Gemini AI (via genkit-ai/google-genai)
- **Authentication**: Requires API key (from environment variables)
- **Model**: `gemini-3-pro-preview` (preview access)
- **Usage**: Text-to-diagram generation with structured output

### Radix UI
- Provides unstyled, accessible component primitives
- Components used: Dialog, Toast, Select, Tabs, Accordion, etc.
- Styled with Tailwind CSS

### Key Files for AI Integration
- `src/ai/genkit.ts`: Genkit instance configuration
- `src/ai/flows/generate-interactive-diagram.ts`: Main diagram generation flow
- `src/ai/flows/suggest-related-concepts.ts`: Related concepts suggestion flow
- `src/lib/actions.ts`: Server action wrapper (`handleGeneration`)

### Environment Setup
- `.env` file required with Google API key
- `package-lock.json` or npm dependencies must be installed
- TypeScript compilation required before running (`typecheck` script)
