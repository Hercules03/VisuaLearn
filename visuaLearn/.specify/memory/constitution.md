<!--
Sync Impact Report - Constitution v2.0.0
==========================================
Version Change: v1.0.0 → v2.0.0 (MINOR - new principles added, expanded sections)
Ratification: 2025-06-13 (original) | Last Amended: 2025-11-24

Modified Principles: None (new document structure established)
Added Sections:
  - Technology Stack (NEW)
  - Performance & Scalability Standards (NEW)
  - Quality & Testing Gates (NEW)

Removed Sections: None

Templates Status:
  - ✅ spec-template.md: No updates required (Constitution checks will be auto-generated)
  - ✅ plan-template.md: No updates required (Technical Context section aligned)
  - ✅ tasks-template.md: No updates required (Testing discipline incorporated)

Follow-up Notes:
  - Export performance targets: Recommend benchmarking X = <5 seconds for typical 10MB+ 3D models
  - Caching strategy: Document retention policy (session-only vs. temp disk storage)
  - Multilingual expansion path: Plan for additional languages beyond EN+JA in v2.1
-->

# visuaLearn Constitution

## Core Principles

### I. Full-Stack Specification-Driven Development

The project adheres to Spec-Driven workflow using Spec Kit. Every feature starts with a specification (spec.md), followed by detailed planning (plan.md), and task breakdowns (tasks.md). This ensures clarity of intent before implementation, independent testability of features, and explicit requirements documentation.

**Non-negotiable requirements**:

- Every user story MUST be independently testable and deliverable as an MVP increment
- Specifications MUST define functional requirements (FR-*), success criteria (SC-*), and edge cases
- Plans MUST document technology stack choices, project structure, and complexity justifications
- Tasks MUST be organized by user story priority (P1, P2, P3) with clear dependencies

**Rationale**: Clear specifications prevent scope creep, enable parallel development, and provide measurable success criteria for QA and stakeholders.

---

### II. React + TypeScript + React-Three-Fiber Frontend Architecture

The frontend MUST use React with TypeScript for type safety and maintainability. Three.js visualization rendering MUST be integrated via React-Three-Fiber to ensure proper React component lifecycle integration, state management, and declarative 3D rendering.

**Non-negotiable requirements**:

- All React components MUST be written in TypeScript (strict mode enforced)
- 3D scene management MUST use React-Three-Fiber (not direct three.js instantiation)
- All props MUST be properly typed; no use of `any` type without explicit justification
- Component state MUST use React hooks (useState, useReducer, useContext)
- Performance: Use React.memo and useMemo for expensive render operations

**Rationale**: TypeScript catches type errors at compile time; React-Three-Fiber ensures React's reactivity model applies to 3D scenes, preventing state synchronization bugs.

---

### III. Node.js + TypeScript Backend Microservice Architecture

The backend MUST be built with Node.js and TypeScript. It serves as the primary application server with a dedicated microservice for Gemini API integration (AI processing). The architecture separates concerns: main server handles frontend routing and data, AI microservice handles generative AI tasks.

**Non-negotiable requirements**:

- Backend server MUST use TypeScript in strict mode for type safety
- All API endpoints MUST define request/response contracts (OpenAPI/JSON Schema)
- AI microservice MUST isolate Gemini API calls and error handling
- Communication between services MUST use well-defined interfaces (e.g., HTTP JSON, message queues)
- All microservices MUST implement structured logging for observability

**Rationale**: Microservice isolation allows independent scaling of AI processing; contracts ensure API stability across frontend/backend evolution.

---

### IV. Multilingual Support (i18next + Backend Translation Pipeline)

Frontend localization MUST use i18next. Backend translation requests (e.g., AI-generated content) MUST go through a centralized translation pipeline (Claude API or translation service). Support for English + Japanese MUST be present from MVP. Additional languages can be added without code changes.

**Non-negotiable requirements**:

- All user-facing strings MUST use i18next namespaces (never hardcoded text)
- Locale MUST be selectable at runtime; default to browser language or EN fallback
- Backend translation pipeline MUST cache translations to minimize API calls
- AI-generated content MUST be translated server-side before delivery to frontend
- Language-specific date/number formatting MUST respect locale (e.g., Intl API)

**Rationale**: Decoupling UI strings from code prevents translation bugs; server-side translation of AI content ensures consistency and reduces frontend complexity.

---

### V. AI Integration via Gemini API (Backend Microservice)

All AI processing MUST route through the backend Gemini microservice. The frontend MUST NOT directly call Gemini; all requests go through backend endpoints. This centralizes API key management, enables request validation, response post-processing, and consistent error handling.

**Non-negotiable requirements**:

- Backend MUST validate all user inputs before sending to Gemini API
- Gemini API calls MUST be wrapped in error handling with user-friendly fallback messages
- All Gemini responses MUST be sanitized before returning to frontend
- Microservice MUST implement rate limiting and quota tracking per user/session
- API keys MUST never be exposed to frontend; use server-side authentication only

**Rationale**: Backend mediation provides security (key isolation), reliability (centralized error handling), and auditability (request logging).

---

### VI. Stateless Results with No Persistent User Database

The system generates AI-powered 3D visualizations on-demand with NO persistent storage of user data or generated results. Each user session is independent. Caching is allowed (session-local, temporary disk) but results MUST NOT be stored in a permanent database. Users MUST explicitly export results if they want to retain them.

**Non-negotiable requirements**:

- NO permanent database for user accounts, session history, or generated results
- Results MUST be stored in-memory during session; deleted on session end
- Temporary caching (e.g., Redis, disk temp folder) is permitted for performance but MUST NOT survive server restart
- Export endpoints (GLB, JSON, SVG) MUST generate on-demand from session state
- Clear user communication: "Results are not saved; export if you want to keep them"

**Rationale**: Eliminates data privacy/compliance complexity; reduces operational overhead; keeps scope focused on generation, not storage. Users are explicitly responsible for retention.

---

### VII. Performance & Scalability: Load-Render-Export Under X Seconds

Initial load, 3D rendering, and model export operations MUST complete within acceptable latency thresholds. The system MUST scale to handle concurrent users without degradation. Performance is a non-negotiable feature, not an afterthought.

**Non-negotiable requirements**:

- Page load (HTML/CSS/JS): MUST complete within 2 seconds on typical broadband (>10Mbps)
- 3D scene render: MUST display interactive scene within 3 seconds of load
- Visualization export (GLB/JSON/SVG): MUST complete within 5 seconds for models <50MB
- Concurrent users: System MUST handle ≥100 simultaneous users without >20% latency increase
- Memory: Client-side rendering MUST use <200MB per user session
- Network: API requests MUST complete within <500ms p95 latency under normal load

**Measurement**: Continuous monitoring via Lighthouse (desktop/mobile), backend timing logs, and user-facing performance metrics in the UI.

**Rationale**: 3D visualization requires fast feedback; poor performance breaks immersion and user engagement. Explicit thresholds enable QA and prevent regression.

---

## Technology Stack & Deployment

### Frontend Stack

- **Framework**: React 18+ with TypeScript (strict mode)
- **3D Rendering**: three.js via React-Three-Fiber
- **Build Tool**: Vite (for fast dev/prod builds)
- **Package Manager**: npm or pnpm
- **Styling**: CSS-in-JS (e.g., Emotion, Styled-Components) or Tailwind CSS
- **Localization**: i18next with backend language support
- **State Management**: React Context + custom hooks (prefer over Redux if feature-scoped)
- **Testing**: Vitest (unit), React Testing Library (component), Playwright (E2E)

### Backend Stack

- **Runtime**: Node.js 18+ with TypeScript (strict mode)
- **Framework**: Express or Fastify (lightweight)
- **API Standard**: OpenAPI/JSON Schema for contract documentation
- **AI Integration**: Gemini API via backend microservice
- **Translation**: Claude API or external translation service (cached)
- **Logging**: Structured JSON logging (e.g., Winston, Pino)
- **Testing**: Jest or Vitest (unit), Supertest (integration)
- **Deployment**: Docker containers; recommend Vercel, Railway, or self-hosted Node.js

### No Database

- **Caching**: Optional Redis/in-memory for session data (not persistent storage)
- **User Sessions**: In-memory or Redis, cleared on logout/timeout
- **Generated Results**: Session-local, not persisted

### DevOps & Observability

- **Version Control**: Git with main/develop branches; feature branches for PRs
- **CI/CD**: GitHub Actions (or similar) - lint, type-check, test on every PR
- **Deployment**: Containerized (Docker); automated on merge to main
- **Monitoring**: Performance metrics via Sentry (errors), Datadog/New Relic (optional), CloudFlare analytics
- **Accessibility**: WCAG 2.1 AA compliance; automated checks via axe-core

---

## Quality & Testing Gates

### Mandatory Quality Checks (All PRs)

1. **Syntax & Type Safety**: TypeScript compilation MUST pass (strict mode, zero errors)
2. **Linting**: ESLint + Prettier MUST pass without warnings
3. **Unit Tests**: MUST pass; target ≥80% code coverage
4. **Integration Tests**: MUST pass for contract (API) changes and AI microservice interactions
5. **Accessibility**: axe-core or similar MUST report zero critical violations
6. **Performance**: Lighthouse score MUST be ≥90 for desktop; ≥70 for mobile (on merge to main)
7. **Security**: No hardcoded secrets; API keys MUST be environment-only; dependency scan for vulnerabilities
8. **Documentation**: API contracts (OpenAPI) MUST be updated; new features MUST include usage examples

### Test Organization

- **Unit Tests**: Test individual functions/components in isolation; ≥80% coverage
- **Integration Tests**: Test API contracts, microservice communication, and end-to-end user journeys
- **E2E Tests**: Playwright tests for critical user flows (visualization generation, export)
- **Performance Tests**: Benchmark 3D render times, export operations; fail if >10% regression

### Pre-Deployment Validation

- All quality gates must pass on main branch
- Manual QA sign-off for visual/UX changes (3D scene quality, accessibility)
- Performance benchmarks MUST show no regression vs. previous release

---

## Accessibility & Mobile-First Design

### Frontend Requirements

- **Responsive Design**: MUST support desktop (1920px+), tablet (768-1024px), mobile (<768px)
- **Mobile Interaction**: Touch-friendly controls; 3D scene navigation MUST work via touch + gestures
- **Keyboard Navigation**: All features MUST be operable via keyboard (no mouse required)
- **Accessibility**: WCAG 2.1 AA minimum; screen reader compatible; alt text for all visuals
- **Performance Mobile**: MUST load and render on 4G networks within thresholds; lazy-load 3D assets

### Backend API Constraints

- Responses MUST be gzip-compressed
- Image/model assets MUST support range requests (for large file streaming)
- API MUST handle slow/unreliable networks gracefully (timeouts, retries)

---

## Export Capabilities & Formats

### Supported Export Formats

- **GLB (glTF Binary)**: Full 3D scene with geometry, materials, animations (via three.js GLTFExporter)
- **JSON**: Scene graph + metadata in JSON format (custom or three.js JSON format)
- **SVG Overlay**: 2D projection of 3D visualization with annotations (lightweight, web-embeddable)

### Export Requirements

- All exports MUST preserve layer information (if applicable)
- User MUST be able to customize export settings (resolution, quality, included layers)
- Exports MUST complete within 5 seconds; large models (>50MB) MUST stream download
- Export file size MUST be minimized without visual quality loss (compression, optimization)

---

## Error Handling & User Communication

### Frontend

- **User-Facing Errors**: Display non-technical messages (e.g., "Failed to generate visualization. Try again.") with optional "Details" for tech-savvy users
- **No Stack Traces**: Never expose server stack traces, internal paths, or sensitive data to users
- **Fallback UI**: If 3D rendering fails, show static preview or error message with recovery action
- **Toast Notifications**: Use for temporary feedback (success, error, warning)
- **Validation Errors**: Highlight form fields with clear, actionable messages

### Backend

- **Structured Logging**: Log all errors with context (request ID, user session, timestamp)
- **Rate Limiting**: Return HTTP 429 with retry-after header when quota exceeded
- **Timeouts**: Gemini API calls MUST timeout after 30 seconds; return user-friendly error
- **Graceful Degradation**: If AI microservice is down, main server MUST stay operational
- **Audit Log**: Log all Gemini API calls (request parameters, response metadata) for cost tracking and debugging

---

## Governance

### Constitution Authority

This Constitution supersedes all other project guidance documents. All code, features, and architectural decisions MUST comply with its principles. Violations require documented exceptions with explicit rationale and shall be reviewed in the next governance cycle.

### Amendment Procedure

1. **Proposal**: Anyone may propose a constitution amendment via GitHub issue (label: `constitution-change`)
2. **Discussion**: Team reviews and discusses implications for 2+ business days
3. **Decision**: Maintainers approve/reject; approved amendments are ratified with versioning (see below)
4. **Implementation**: Migration plan MUST be documented; timeline for existing code to comply is set (typically 1-2 sprints)
5. **Enforcement**: CI/CD gates validate new constitution immediately; legacy code is gradually refactored

### Versioning Policy

- **MAJOR**: Backward-incompatible principle changes or removals (e.g., switching from React to Vue)
- **MINOR**: New principles or sections added; guidance expanded (existing principles unmodified)
- **PATCH**: Clarifications, wording fixes, typos (no semantic change)

**Current Version Strategy**: Start at v2.0.0; increment MINOR for new language support or performance threshold changes; increment MAJOR if core tech stack is replaced.

### Compliance Review

- **Quarterly**: Maintainers review all merged PRs against constitution compliance
- **Annual**: Full project architecture audit against all principles; report published
- **Ad-hoc**: Any team member may flag suspected violations in PR reviews

### Quality Gate Enforcement

All CI/CD pipelines MUST include automated checks for:

- TypeScript compilation (strict mode)
- ESLint/Prettier formatting
- Lighthouse performance (desktop ≥90, mobile ≥70)
- axe-core accessibility (zero critical violations)
- Test coverage (≥80%)
- API contract validation (OpenAPI compliance)

**Failure Resolution**: PRs failing quality gates MUST be fixed or explicitly exempted with rationale in commit message.

---

## Appendix: Spec-Driven Workflow Integration

This Constitution drives the Spec Kit workflow templates:

- **spec-template.md**: Constitution principles constrain feature scope (e.g., stateless design, performance budgets)
- **plan-template.md**: Constitution Check gate validates alignment (tech stack, accessibility, performance targets)
- **tasks-template.md**: Task phases must reflect Constitution testing discipline (unit + integration + E2E)

All features MUST pass Constitution Check before Phase 0 research and again before Phase 2 implementation.

---

**Version**: 2.0.0 | **Ratified**: 2025-06-13 | **Last Amended**: 2025-11-24
