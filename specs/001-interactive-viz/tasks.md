# Implementation Tasks: AI-Powered Interactive 3D Concept Visualizer

**Feature Branch**: `001-interactive-viz`
**Created**: 2025-11-24
**Task Generator**: /speckit.tasks
**Total Tasks**: 72 | **P1**: 28 | **P2**: 18 | **P3**: 12 | **Infrastructure**: 14

---

## Task Organization & Execution Strategy

### Phase Overview

| Phase | Purpose | Dependencies | Est. Tasks | Duration |
|-------|---------|--------------|-----------|----------|
| **Phase 1: Setup & Infrastructure** | Environment, build tools, project initialization | None | 14 | 2-3 days |
| **Phase 2: Foundational Services** | Shared backend services, middleware, caching | Phase 1 | 10 | 3-4 days |
| **Phase 3: User Story 1 (P1) - Student Learns** | Core MVP: input form, 3D viewer, controls | Phases 1-2 | 28 | 5-7 days |
| **Phase 4: User Story 2 (P2) - Teacher Exports** | Export modal, GLB/JSON/SVG generation | Phases 1-3 | 18 | 4-5 days |
| **Phase 5: User Story 3 (P3) - Researcher Explores** | Localization, depth levels, advanced features | Phases 1-4 | 12 | 3-4 days |
| **Phase 6: Polish & Cross-Cutting Concerns** | Testing, optimization, accessibility, docs | All phases | 10 | 3-4 days |

### MVP Scope
**P1 Only** (User Story 1: Student Learns) is sufficient for MVP validation and can be released independently. P2 and P3 are fully supported but represent Phase 2 enhancements.

### Parallel Execution Opportunities
- [P] Tasks marked with [P] can run in parallel with non-blocked siblings
- Frontend and backend components can be developed simultaneously once Phase 2 is complete
- Localization (P3) can progress in parallel with P1 and P2 after Phase 2

---

## Phase 1: Setup & Infrastructure

### Project Initialization & Build Tools

- [ ] **T101** [Setup] Initialize frontend project with Vite + React 18 + TypeScript in `frontend/` directory with proper tsconfig.json (strict mode), package.json with React 18+, React-Three-Fiber, three.js, i18next, axios

- [ ] **T102** [Setup] Initialize backend project with Node.js 18+ + Express/Fastify + TypeScript in `backend/` directory with proper tsconfig.json, package.json with Express, axios, dotenv, cors, helmet, pino/winston

- [ ] **T103** [P] [Setup] Create root `package.json` with monorepo structure, scripts for `npm run dev` (both frontend and backend), `npm run build`, `npm run test`, shared tsconfig references

- [ ] **T104** [Setup] Create `.env.example` files for both frontend (`VITE_API_URL`) and backend (`GEMINI_API_KEY`, `CLAUDE_API_KEY`, `REDIS_URL`, `PORT`, `NODE_ENV`)

- [ ] **T105** [P] [Setup] Set up ESLint + Prettier configuration across frontend and backend with consistent TypeScript linting rules, code formatting, and pre-commit hooks

- [ ] **T106** [Setup] Create Docker setup: write `backend/Dockerfile` for containerized deployment with Node.js 18 base image, multi-stage build, healthcheck endpoint

- [ ] **T107** [P] [Setup] Set up CI/CD pipelines in `.github/workflows/`: `lint-test.yml` (lint, type-check, unit tests on PR) and `deploy.yml` (build, push to container registry on merge to main)

- [ ] **T108** [Setup] Create GitHub branch protection rules for `main`: require PR reviews, passing CI checks, no direct pushes except releases

### Type Definitions & Shared Interfaces

- [ ] **T109** [P] [Setup] Create TypeScript type definitions file `backend/src/types/index.ts` with interfaces: `ConceptRequest`, `AnimationSpec`, `ExplanationText`, `ExportPackage`, `APIResponse<T>`, `APIError`

- [ ] **T110** [Setup] Create TypeScript type definitions file `frontend/src/types/index.ts` with interfaces: `Concept`, `Animation3D`, `ControlState`, `ExportOptions`, `UIState`

### Git & Documentation Setup

- [ ] **T111** [P] [Setup] Create comprehensive `.gitignore` files for both frontend and backend (node_modules, dist, .env, .env.local, build artifacts, OS files)

- [ ] **T112** [Setup] Create root `README.md` with project overview, quick start instructions, architecture diagram, and links to spec/plan documents

- [ ] **T113** [Setup] Create `CONTRIBUTING.md` with development guidelines, branch naming conventions, commit message format, PR process

- [ ] **T114** [P] [Setup] Initialize git flow: create feature branch `001-interactive-viz` from `main`, set branch as development target for all PRs in this feature

---

## Phase 2: Foundational Services & Middleware

### Backend Core Services

- [ ] **T201** [Service] Implement `backend/src/services/InputValidator.ts`: validate concept length (>2 words), blocklist keyword check (bomb, exploit, malware, attack method + synonyms), max 200 chars, return specific error messages for each validation failure

- [ ] **T202** [Service] Implement `backend/src/services/CacheManager.ts`: session-local in-memory cache with TTL support, LRU eviction, support for cache layers (request-level 5min, session 1hr, global 1 week, translation 1 week), methods: get, set, delete, clear

- [ ] **T203** [P] [Service] Implement `backend/src/services/ErrorHandler.ts`: centralized error handling middleware, user-friendly error messages for: validation errors (400), rate limit exceeded (429), Gemini API timeout (503), malformed responses. Never expose technical details

- [ ] **T204** [Service] Implement `backend/src/middleware/RateLimiter.ts`: track requests per session ID (via cookie or header), enforce 10 requests/minute limit, return HTTP 429 with retry-after header when exceeded, session-based tracking (not IP-based for MVP)

- [ ] **T205** [P] [Service] Implement `backend/src/services/AnimationSpecValidator.ts`: validate Gemini response is valid JSON, conforms to three.js Object3D schema, contains at least one geometry and one material, optional animations, return clear error if invalid

### Backend API Foundation

- [ ] **T206** [P] [API] Create `backend/src/app.ts`: Express/Fastify server setup with middleware: CORS (frontend origin), helmet for security, body parser (JSON), session middleware (generate UUID session ID, bind to HttpOnly cookie), error handler middleware, logging

- [ ] **T207** [API] Create `backend/src/routes/index.ts`: route definitions for POST `/api/concepts` and POST `/api/export` with request/response validation using schemas

- [ ] **T208** [API] Create health check endpoint `GET /health`: return `{ status: "ok", timestamp: ISO8601 }` for deployment verification

### Frontend Foundation

- [ ] **T209** [P] [Frontend] Set up `frontend/src/config/i18n.ts`: i18next initialization with namespaces (common, messages, validation, errors), language detection (browser language), fallback to English, runtime language switching via localStorage, load translations from `public/locales/{en,ja}/`

- [ ] **T210** [Frontend] Create i18next translation files: `frontend/public/locales/en/common.json` and `frontend/public/locales/ja/common.json` with complete namespace keys for all UI strings (buttons, labels, error messages, help text)

---

## Phase 3: User Story 1 (P1) - Student Learns Concept

### P1 Backend Services: Gemini Integration

- [ ] **T301** [P1] [Service] Implement `backend/src/services/GeminiService.ts`: wrap Gemini API with structured prompt, request three components: (1) plain-text explanation (max 1000 words), (2) three.js JSON spec, (3) optional embed code. Handle 30-second timeout, parse JSON response, return normalized object with explanation + spec

- [ ] **T302** [P1] [Service] Implement `backend/src/controllers/ConceptController.ts`: POST `/api/concepts` handler that: validates input via InputValidator, checks cache (CacheManager), calls GeminiService if cache miss, validates spec via AnimationSpecValidator, returns `{ id, explanationText, animationSpec, embedCodeSnippet }`

- [ ] **T303** [P1] [Service] Implement `backend/src/services/TranslationService.ts` (stub for P1, full for P2): for P1, return English text only (no translation). For P3/P2, call Claude API if language != EN, cache translations, fallback to EN on failure

### P1 Frontend Components: Input & Validation

- [ ] **T304** [P1] [P] [Component] Create `frontend/src/components/ConceptInputForm.tsx`: form with text input field (max 200 chars with counter), depth selector dropdown (intro/intermediate/advanced), language selector (EN/JA with flag icons), submit button, real-time validation feedback, disabled submit when validation fails

- [ ] **T305** [P1] [Component] Create `frontend/src/components/ErrorDisplay.tsx`: reusable error message component with icon, clear text, dismiss button, auto-dismiss after 5 seconds for non-critical errors (rate limit shows longer)

- [ ] **T306** [P1] [Component] Create `frontend/src/components/LoadingSpinner.tsx`: centered animated spinner with "Generating visualization..." status text, used during Gemini API call

### P1 Frontend Services & Utilities

- [ ] **T307** [P1] [Service] Implement `frontend/src/services/ConceptService.ts`: API client for POST `/api/concepts` with axios, handle errors and status codes, parse response into frontend types, retry logic for transient failures

- [ ] **T308** [P1] [Utility] Create `frontend/src/utils/validation.ts`: client-side validation functions: isValidConcept (>2 words), validateInput (max length, no special chars), format messages for display

### P1 Frontend 3D Viewer Component

- [ ] **T309** [P1] [Component] Create `frontend/src/components/ThreeJSViewer.tsx`: React-Three-Fiber canvas component that: loads three.js JSON spec from prop, renders scene with proper camera (perspective), enables orbit controls (rotation, zoom, pan), detects WebGL availability, shows fallback message if unavailable

- [ ] **T310** [P1] [Component] Create `frontend/src/components/CameraControls.tsx`: reusable orbit controls component using @react-three/drei `OrbitControls`, smooth mouse/touch interaction, keyboard shortcuts (arrow keys), reasonable camera initial position

- [ ] **T311** [P1] [P] [Component] Implement three.js JSON loader in ThreeJSViewer: use `THREE.ObjectLoader` or custom loader to parse JSON spec, create scene graph, apply geometries and materials, attach animations, handle missing data gracefully

### P1 Frontend Controls & Animation

- [ ] **T312** [P1] [Component] Create `frontend/src/components/ControlsPanel.tsx`: animation playback controls with: play/pause button, speed slider (0.5x to 2x with discrete steps), progress bar with current time / total time, layer toggle buttons (dynamically generated from scene), real-time updates during playback

- [ ] **T313** [P1] [Component] Create `frontend/src/components/LayerToggle.tsx`: individual layer visibility toggle component, checkbox + label with layer name, onChange handler to update scene visibility, visual feedback for toggled state

- [ ] **T314** [P1] [Service] Implement animation playback logic in `frontend/src/services/AnimationPlayer.ts`: play/pause state management, speed multiplier application to animation clips, progress tracking, layer visibility toggling, integrates with three.js AnimationMixer

### P1 Frontend Explanation Display

- [ ] **T315** [P1] [Component] Create `frontend/src/components/ExplanationPanel.tsx`: display AI-generated text explanation with: auto-formatting (headings preserved, bullet points rendered, line breaks preserved), max 1000 words enforced, responsive width on desktop/tablet/mobile

- [ ] **T316** [P1] [Component] Create `frontend/src/components/SessionWarning.tsx`: persistent banner with message "Results are not saved. Export if you want to keep them." dismissed by user preference (localStorage key), reappears on new session

### P1 Frontend App Layout & State Management

- [ ] **T317** [P1] [P] [Component] Create `frontend/src/App.tsx`: main layout component with: ConceptInputForm at top (or sidebar on desktop), loading spinner during generation, ThreeJSViewer takes center/right, ControlsPanel below viewer, ExplanationPanel beside/below, error display at top, session warning banner

- [ ] **T318** [P1] [Service] Create `frontend/src/hooks/useConceptState.ts`: React hook for managing concept generation state (loading, error, data), handles API calls, caching, error handling, integrates with ConceptService

- [ ] **T319** [P1] [P] [Component] Create `frontend/src/index.tsx`: React app entry point with i18n initialization, error boundary, theme provider if applicable

### P1 Responsive Design & Accessibility (Initial)

- [ ] **T320** [P1] [Component] Create `frontend/src/styles/layout.css`: responsive layout styles using CSS Grid/Flexbox for: desktop (1920px+: two-column with viewer on right, form+controls on left), tablet (768-1024px: stacked), mobile (<768px: vertical stack), touch-friendly button sizes (48px minimum)

- [ ] **T321** [P1] [P] [Component] Add keyboard navigation to all interactive components: Tab order for form inputs, buttons, layer toggles. Enter/Space to activate buttons. Arrow keys for sliders. ARIA labels for all controls

- [ ] **T322** [P1] [Accessibility] Create `frontend/src/components/SkipLink.tsx`: "Skip to main content" link for keyboard users, visually hidden by default, visible on focus, links to main viewer area

### P1 Testing (Core Happy Path)

- [ ] **T323** [P1] [Test] Write unit tests for `InputValidator.ts`: valid concepts (2+ words), invalid concepts (single word, blocklist), edge cases (exactly 2 words, max length, special chars)

- [ ] **T324** [P1] [Test] Write unit tests for `ConceptService.ts`: successful API call, error handling, response parsing, timeout handling

- [ ] **T325** [P1] [Test] Write component tests for `ConceptInputForm.tsx`: rendering, input validation feedback, form submission, state updates

- [ ] **T326** [P1] [P] [Test] Write E2E test for P1 happy path using Playwright: load app, enter concept, submit, verify loading state, verify 3D viewer appears, verify controls work (play/pause, speed slider), verify explanation text displays

---

## Phase 4: User Story 2 (P2) - Teacher Exports

### P2 Backend Services: Export Generation

- [ ] **T401** [P2] [Service] Implement `backend/src/services/ExportService.ts`: generate GLB, JSON, and SVG from animation spec stored in cache. Methods: generateGLB (use three.js GLTFExporter), generateJSON (scene.toJSON()), generateSVG (three.js SVGRenderer or custom 2D projection), validateExportFormat

- [ ] **T402** [P2] [P] [Service] Implement file streaming for large exports (>50MB): use HTTP 206 range requests, set content-length header, stream file chunks, handle resume/partial downloads

- [ ] **T403** [P2] [Controller] Implement `backend/src/controllers/ExportController.ts`: POST `/api/export` handler that: validates conceptId exists in cache, validates format (glb/json/svg), calls ExportService, returns download URL or streams file directly

### P2 Frontend Components: Export Modal

- [ ] **T404** [P2] [P] [Component] Create `frontend/src/components/ExportModal.tsx`: modal dialog with: format selector (GLB, JSON, SVG with descriptions), resolution dropdown (720p, 1080p, 2k for GLB/SVG), annotation toggle checkbox, layer selection checkboxes (filter which layers to include), customization preview, download button

- [ ] **T405** [P2] [Component] Create `frontend/src/components/FormatSelector.tsx`: radio button group for export formats with icons/descriptions: GLB (3D model format, 3D viewers), JSON (scene graph, embedding), SVG (2D slides, presentations)

- [ ] **T406** [P2] [Component] Create `frontend/src/components/ResolutionSelector.tsx`: dropdown for output resolution (720p, 1080p, 2k), description of output quality/file size trade-off

- [ ] **T407** [P2] [P] [Component] Create `frontend/src/components/LayerSelector.tsx`: multi-select checkboxes for scene layers (dynamically populated), "Select All" / "Deselect All" buttons, visual feedback for selection count

### P2 Frontend Export Workflow

- [ ] **T408** [P2] [Component] Create `frontend/src/components/ExportButton.tsx`: button in ControlsPanel that opens ExportModal when clicked, disabled if no visualization loaded, loading state during export

- [ ] **T409** [P2] [Service] Implement `frontend/src/services/ExportService.ts`: API client for POST `/api/export`, handle file download (using `fetch` blob + `download` attribute), generate filename (concept-depth-format-timestamp.ext), progress tracking, error handling

- [ ] **T410** [P2] [P] [Service] Implement file download handling in `frontend/src/utils/downloadFile.ts`: create blob, generate filename with timestamp, trigger browser download via temporary anchor element, cleanup

### P2 Export Validation & Testing

- [ ] **T411** [P2] [Test] Write tests for `ExportService.ts`: GLB generation valid glTF 2.0, JSON generation valid JSON schema, SVG generation valid SVG, file size validation

- [ ] **T412** [P2] [Test] Write component tests for `ExportModal.tsx`: rendering formats/resolutions/options, form validation, selection state tracking, download trigger

- [ ] **T413** [P2] [P] [Test] Write E2E test for P2 export flow using Playwright: generate concept, click export, select format, customize options, verify download file exists, verify file format (GLB openable in viewer, JSON parseable, SVG renderable)

---

## Phase 5: User Story 3 (P3) - Researcher Explores

### P3 Backend Services: Translation Pipeline

- [ ] **T501** [P3] [Service] Complete `backend/src/services/TranslationService.ts` (started in Phase 1): call Claude API for EN→JA translation, cache translations in CacheManager (1 week TTL), fallback to English on translation failure, return appropriately

- [ ] **T502** [P3] [P] [Service] Implement translation controller in `backend/src/controllers/TranslationController.ts` (optional): POST `/api/translate` endpoint for batch translation requests if needed for P3 advanced features

### P3 Gemini Prompt Enhancement

- [ ] **T503** [P3] [Service] Enhance `GeminiService.ts` prompt for depth levels: modify prompt based on depth parameter (intro: simple 5-step explanation, intermediate: 8-10 steps with detailed mechanics, advanced: detailed explanation with mathematical concepts, academic references)

- [ ] **T504** [P3] [P] [Service] Implement Gemini response validation: ensure explanation text matches requested depth level (complexity heuristics: word count, terminology, structure), reject responses that don't match depth requirement

### P3 Frontend: Localization (Japanese)

- [ ] **T505** [P3] [L10n] Complete i18next translations: all UI strings in `public/locales/ja/common.json` with fluent Japanese (not machine-translated), covering: form labels, button text, error messages, help text, accessibility labels

- [ ] **T506** [P3] [P] [L10n] Add date/time formatting for non-English locales: time format, date format, number format (if applicable) using i18next-intl or built-in formatting

### P3 Frontend: Depth Level Display

- [ ] **T507** [P3] [Component] Enhance `ConceptInputForm.tsx` for P3: depth selector with descriptions ("Intro: Basic concepts", "Intermediate: Standard depth", "Advanced: Expert level"), depth selection persists in localStorage across sessions

- [ ] **T508** [P3] [P] [Component] Create `frontend/src/components/DepthLevelInfo.tsx`: informational tooltip/popover explaining each depth level, shown on hover/click, explains what to expect in explanation and visualization

### P3 Frontend: Advanced Visualization Features

- [ ] **T509** [P3] [Component] Enhance `ControlsPanel.tsx` for P3: add step-by-step navigation (if animation has discrete steps), jump to step buttons, per-step annotations/descriptions, timeline visualization showing steps

- [ ] **T510** [P3] [P] [Component] Create `frontend/src/components/StepAnnotations.tsx`: display annotation text for current animation step, update in real-time as animation plays, include physics principles or mathematical notation if applicable

- [ ] **T511** [P3] [Component] Enhance `ExportModal.tsx` for P3: include annotations in export toggle (checked by default for advanced depth exports), metadata inclusion option (include step descriptions in JSON/SVG exports)

### P3 Advanced Features Testing

- [ ] **T512** [P3] [Test] Write E2E tests for P3 features using Playwright: select advanced depth level, generate complex concept, verify detailed explanation, verify Japanese localization accuracy (if possible), export with annotations, verify annotations in exported file

---

## Phase 6: Polish & Cross-Cutting Concerns

### Performance Optimization

- [ ] **T601** [P] [Perf] Audit frontend bundle size using `npm run build` + webpack bundle analyzer, identify and eliminate unused dependencies, lazy-load non-critical components (export modal), code-split three.js loaders

- [ ] **T602** [Perf] Optimize 3D rendering performance: implement LOD (Level of Detail) for complex scenes, test rendering on mid-range mobile devices (iPad Air, Galaxy Tab S5), achieve 60fps target, profile with DevTools performance tab

- [ ] **T603** [P] [Perf] Implement caching headers for static assets: frontend build outputs with cache-busting, backend cache-control headers for API responses, Redis cache TTL management

### Testing Completeness

- [ ] **T604** [Test] Increase unit test coverage to ≥80%: measure with `npm run test -- --coverage`, add tests for edge cases, error handling, state transitions

- [ ] **T605** [P] [Test] Write integration tests for backend API endpoints: test full flow from request to response, verify error handling (validation errors, API timeouts, rate limiting)

- [ ] **T606** [Test] Add cross-browser E2E tests with Playwright: test on Chrome, Firefox, Safari (if applicable), verify responsive design on tablet/mobile viewport sizes

### Accessibility Audit & Enhancement

- [ ] **T607** [A11y] Run axe-core accessibility audit on frontend app: identify and fix violations (color contrast, missing labels, keyboard navigation), achieve zero critical violations

- [ ] **T608** [P] [A11y] Test with screen reader (NVDA/JAWS/VoiceOver): verify all UI elements are announced correctly, form labels associated properly, 3D viewer has accessible fallback text

- [ ] **T609** [A11y] Verify Lighthouse accessibility score ≥95: run audit in DevTools, fix remaining issues (WCAG 2.1 AA compliance)

### Documentation & Knowledge Transfer

- [ ] **T610** [Docs] Create API documentation (OpenAPI/Swagger): document POST `/api/concepts` and POST `/api/export` endpoints with request/response examples, error codes, rate limiting

- [ ] **T611** [P] [Docs] Create developer guide: component architecture, service patterns, styling conventions, how to add new features, troubleshooting common issues

- [ ] **T612** [Docs] Create deployment guide: Docker build, environment variables, Redis setup, deployment to Vercel (frontend) and AWS ECS/Railway (backend)

### Production Readiness

- [ ] **T613** [P] [DevOps] Set up monitoring & logging: structured logging in backend (Pino/Winston), error tracking (Sentry or similar), performance monitoring (frontend RUM if applicable)

- [ ] **T614** [DevOps] Create production environment checklist: verify API keys are not in code, environment variables are externalized, CORS origin is set correctly, rate limiting is active, Redis is connected if used

---

## Task Dependencies & Execution Order

### Critical Path (Must Complete in Order)

1. **Phase 1** (Setup) → **T101-T114** (all infrastructure)
2. **Phase 2** (Foundational) → **T201-T210** (all services)
3. **Phase 3** (P1) → **T301-T326** (student learns MVP)
4. **Phase 4** (P2) → **T401-T413** (exports)
5. **Phase 5** (P3) → **T501-T512** (localization)
6. **Phase 6** (Polish) → **T601-T614** (quality & deployment)

### Parallelizable Tasks (Can Start After Phase 2)

- Frontend components (**T304-T322**) can develop in parallel with backend services (**T301-T303**)
- Testing (**T323-T326**, **T411-T413**, **T512**, **T604-T606**) can progress once implementation code exists
- Localization (**T505-T511**) can progress after core components exist
- Performance & accessibility audits (**T601-T609**) can run after Phase 3 minimum

---

## Implementation Strategy & Best Practices

### Task Execution Guidelines

1. **Read Implementation Plan First**: Each developer reads `/specs/001-interactive-viz/plan.md` to understand architecture
2. **Follow Data Model**: Use entity types from `data-model.md` when creating TypeScript interfaces
3. **Validate Input**: All user input validated per `spec.md` Clarification Q1 (>2 words, blocklist)
4. **Test as You Go**: Don't wait for Phase 6; write unit tests during implementation
5. **Commit Often**: Small commits with clear messages, reference task ID in commit (`T###: brief description`)

### Quality Standards

- **Type Safety**: No `any` types; strict TypeScript compilation
- **Error Handling**: No silent failures; all errors logged and returned with user-friendly messages
- **Testing**: Minimum 80% unit test coverage for critical services
- **Accessibility**: WCAG 2.1 AA compliance from start, not retrofitted

### File Organization

```
frontend/
  src/
    components/        # React components (T304-T322)
    services/          # API clients (T307, T409, T410)
    hooks/            # Custom hooks (T318)
    utils/            # Utilities (T308)
    config/           # Configuration (T209)
    styles/           # CSS (T320)
    types/            # TypeScript types (T110)
    App.tsx           # Main component (T317)
    index.tsx         # Entry point (T319)

backend/
  src/
    services/         # Business logic (T201-T204, T301-T303, T401-T504)
    controllers/      # Route handlers (T302, T403)
    middleware/       # Express middleware (T204, T206)
    routes/           # Route definitions (T207)
    types/            # TypeScript types (T109)
    app.ts            # Server setup (T206)
    index.ts          # Entry point
```

---

## Success Criteria for Task Completion

Each task is complete when:

1. ✅ Code is written and committed to feature branch
2. ✅ Unit tests pass (or E2E test passes for UI tasks)
3. ✅ TypeScript strict mode passes with no errors
4. ✅ ESLint passes with no warnings
5. ✅ Code follows established patterns from other tasks
6. ✅ Related documentation is updated if applicable

---

## Notes

- **MVP Scope**: Release P1 (User Story 1) independently once Phase 3 is complete. P2 and P3 are enhancements but fully supported.
- **No Fallbacks**: Per SuperClaude principles, no default values or fallback data. Raise errors explicitly.
- **Stateless by Design**: No persistent storage; session-local caching only. All state ephemeral.
- **API-First**: Backend endpoints defined before frontend implementation. Use OpenAPI contracts.
- **Performance Target**: Page load <2s, 3D render <3s, export <5s, Lighthouse 90/70, 100 concurrent users.

---

## Next Steps (Post-Task Generation)

1. Update agent context: `/bash .specify/scripts/bash/update-agent-context.sh claude`
2. Validate task format: All tasks follow `- [ ] [T###] [P?] [US#?] Description with file path`
3. Verify user story independence: Each story testable without others
4. Document MVP scope: P1 is minimum viable product
5. Provide task summary: 72 tasks, distributed by phase and story
