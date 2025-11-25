# visuaLearn: AI-Powered Interactive 3D Concept Visualizer

**Status**: 🚀 Active Development (Phase 1-2 Infrastructure)
**Version**: 1.0.0
**Last Updated**: 2025-11-24

---

## Overview

visuaLearn is an interactive web application that transforms complex educational concepts into animated 3D visualizations with AI-generated explanations. Users input any concept (e.g., photosynthesis, DDoS attacks, quantum entanglement), and the system instantly generates:

- 📝 **Clear text explanation** (under 1000 words)
- 🎨 **Animated 3D visualization** with step-by-step animations
- 🎮 **Interactive controls** (play/pause, speed adjustment, camera rotation, layer toggling)
- 🌍 **Multilingual support** (English + Japanese)
- 💾 **Export options** (GLB, JSON, SVG formats)

### Key Features

- ✅ **No user accounts required** - instant access
- ✅ **Real-time generation** via Gemini API (3-5 seconds)
- ✅ **Session-local caching** for instant re-access
- ✅ **Responsive design** - works on desktop, tablet, mobile
- ✅ **WCAG 2.1 AA accessibility** compliance
- ✅ **Zero persistent storage** - fully stateless by design

---

## Quick Start

### Prerequisites

- **Node.js**: 18+ ([download](https://nodejs.org/))
- **npm**: 9+ or **pnpm** 8+
- **API Keys**:
  - [Google Gemini API](https://ai.google.dev/) (free tier available)
  - [Claude API](https://console.anthropic.com/) (optional, for translations)

### Installation

```bash
# Clone repository
git clone <repo-url>
cd visuaLearn

# Install dependencies for monorepo
npm install

# Configure environment variables
cp frontend/.env.example frontend/.env.local
cp backend/.env.example backend/.env.local

# Edit .env.local files with your API keys
```

### Running Locally

**Terminal 1: Frontend (Vite dev server)**
```bash
npm run dev -w frontend
# Opens http://localhost:5173
```

**Terminal 2: Backend (Node.js API)**
```bash
npm run dev -w backend
# Runs on http://localhost:3000
```

**Terminal 3 (Optional): Redis Cache**
```bash
redis-server
# Runs on localhost:6379
```

Or use all at once:
```bash
npm run dev
# Starts both frontend and backend concurrently
```

### Verify Setup

1. **Frontend**: Open http://localhost:5173 → should see input form
2. **Backend**: GET http://localhost:3000/health → should return `{ status: "ok" }`
3. **Test Concept**: Enter "photosynthesis", select depth, click submit → wait 3-5 seconds for 3D visualization

---

## Project Structure

```
visuaLearn/
├── frontend/                    # React 18 + TypeScript + Vite
│   ├── src/
│   │   ├── components/         # React components
│   │   ├── services/           # API clients
│   │   ├── config/             # i18next localization
│   │   ├── types/              # TypeScript interfaces
│   │   └── App.tsx
│   ├── public/locales/         # Translation files (en, ja)
│   ├── tsconfig.json
│   └── vite.config.ts
│
├── backend/                     # Node.js + Express + TypeScript
│   ├── src/
│   │   ├── services/           # Business logic (Gemini, translation, etc.)
│   │   ├── controllers/        # Route handlers
│   │   ├── middleware/         # Express middleware
│   │   ├── routes/             # API endpoints
│   │   ├── types/              # TypeScript interfaces
│   │   └── app.ts
│   ├── tests/                  # Unit, integration, E2E tests
│   ├── Dockerfile
│   └── tsconfig.json
│
├── specs/                       # Specification documents
│   └── 001-interactive-viz/
│       ├── spec.md             # Feature specification
│       ├── plan.md             # Implementation plan
│       ├── data-model.md       # Entity definitions
│       ├── quickstart.md       # Developer guide
│       └── tasks.md            # Task breakdown
│
├── .github/workflows/          # CI/CD pipelines
│   ├── lint-test.yml
│   └── deploy.yml
│
├── .eslintrc.json              # Linting rules
├── .prettierrc                 # Code formatting
├── .gitignore
├── package.json                # Monorepo root
└── README.md
```

---

## Technology Stack

### Frontend
- **React 18** + **TypeScript** with strict mode
- **React-Three-Fiber** (R3F) for declarative 3D rendering
- **three.js r156** for 3D graphics
- **i18next** for multilingual support (EN, JA)
- **Vite** for fast development and optimized builds
- **Vitest** + **React Testing Library** for testing

### Backend
- **Node.js 18+** + **TypeScript**
- **Express.js** for HTTP API
- **Gemini API** for AI generation
- **Claude API** for translation (EN ↔ JA)
- **Pino** for structured logging
- **In-memory or Redis** for session caching

### DevOps
- **Docker** for containerization
- **GitHub Actions** for CI/CD
- **Vercel** for frontend hosting (recommended)
- **AWS ECS / Railway / Render** for backend hosting

---

## Development Workflow

### Scripts

```bash
# Development
npm run dev              # Start both frontend + backend
npm run dev -w frontend # Frontend only
npm run dev -w backend  # Backend only

# Building
npm run build           # Build both frontend + backend
npm run build -w frontend
npm run build -w backend

# Testing
npm run test            # Run all tests
npm run test:coverage   # Generate coverage reports

# Code Quality
npm run lint            # Check code style
npm run lint:fix        # Auto-fix style issues
npm run format          # Format code with Prettier
npm run type-check      # Check TypeScript types
```

### Branching Convention

- **main**: Production-ready code
- **develop**: Integration branch
- **feature/\***: Feature branches (e.g., `feature/p1-student-learns`)
- **bugfix/\***: Bug fix branches

### Commit Messages

```
[T###] Brief description

Detailed explanation if needed.

Closes #issue-number
```

Example: `[T101] Initialize frontend project with Vite + React 18`

### Pull Requests

1. Create feature branch from `develop`
2. Implement feature with tests
3. Ensure `npm run lint`, `npm run type-check`, `npm run test` pass
4. Push to remote and create PR
5. Require at least 1 approval before merging
6. Merge to `develop`, then promote to `main` for releases

---

## API Endpoints

### Concept Generation

**POST /api/concepts**

```json
{
  "concept": "photosynthesis",
  "depth": "intro",
  "language": "en"
}
```

**Response (200 OK)**
```json
{
  "id": "uuid-here",
  "explanationText": "Photosynthesis is the process...",
  "animationSpec": { /* three.js JSON object */ },
  "embedCodeSnippet": "..."
}
```

### Export

**POST /api/export**

```json
{
  "conceptId": "uuid-here",
  "format": "glb",
  "options": {
    "resolution": "1080p",
    "includeAnnotations": true
  }
}
```

**Response (200 OK)**
```
Binary GLB file download
```

### Health Check

**GET /health**

**Response (200 OK)**
```json
{
  "status": "ok",
  "timestamp": "2025-11-24T12:00:00Z"
}
```

---

## Specification & Architecture

- 📋 **Feature Spec**: [specs/001-interactive-viz/spec.md](./specs/001-interactive-viz/spec.md)
  - 20 functional requirements, 15 success criteria, 7 edge cases

- 🏗️ **Implementation Plan**: [specs/001-interactive-viz/plan.md](./specs/001-interactive-viz/plan.md)
  - Architecture diagrams, tech stack rationale, module responsibilities

- 📊 **Data Model**: [specs/001-interactive-viz/data-model.md](./specs/001-interactive-viz/data-model.md)
  - Entity definitions, state machine, caching strategy

- 🚀 **Quickstart**: [specs/001-interactive-viz/quickstart.md](./specs/001-interactive-viz/quickstart.md)
  - Developer onboarding guide

- ✅ **Tasks**: [specs/001-interactive-viz/tasks.md](./specs/001-interactive-viz/tasks.md)
  - 72 actionable tasks across 6 phases

---

## MVP Release Plan

### Phase 1: Setup & Infrastructure ✅ (In Progress)
- Project initialization (Vite, Node.js, Docker)
- Build tools and CI/CD pipelines
- TypeScript configurations

### Phase 2: Foundational Services (Next)
- Core backend services (InputValidator, CacheManager, ErrorHandler)
- API foundation and middleware
- i18next localization setup

### Phase 3: User Story 1 - Student Learns (P1 MVP)
- Concept input form with validation
- React-Three-Fiber 3D viewer
- Animation playback controls
- Explanation display panel

**🎯 MVP Release Gate**: Phases 1-3 complete = **Minimum viable product**

### Phase 4: User Story 2 - Teacher Exports (P2)
- Export modal with format selection
- GLB/JSON/SVG generation

### Phase 5: User Story 3 - Researcher Explores (P3)
- Advanced depth levels
- Japanese localization
- Step-by-step annotations

### Phase 6: Polish & Quality
- Performance optimization
- Accessibility audit (WCAG 2.1 AA)
- Comprehensive testing

---

## Testing

### Unit Tests
```bash
npm run test
npm run test:coverage
```

**Target Coverage**: ≥80% for critical services

### Integration Tests
```bash
npm run test:integration -w backend
```

### E2E Tests (Playwright)
```bash
npm run test:e2e
```

---

## Deployment

### Frontend (Vercel)
```bash
vercel --prod
```

### Backend (Docker to AWS ECS / Railway)
```bash
# Build Docker image
docker build -t visualearn-api .

# Push to registry
docker push <registry>/visualearn-api:latest

# Deploy via ECS/Railway CLI
```

---

## Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| "Cannot find module" | Missing dependencies | `npm install` in correct directory |
| `GEMINI_API_KEY` undefined | .env.local not configured | `cp .env.example .env.local` + add key |
| CORS error | Frontend/backend mismatch | Verify `VITE_API_URL` matches backend URL |
| "WebGL not available" | Browser doesn't support WebGL | Use modern browser or export as SVG |
| Build fails with TypeScript errors | Strict mode violations | Fix type errors per ESLint output |

---

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for detailed guidelines on:
- Development setup
- Branch naming conventions
- Commit message format
- PR process
- Code style expectations

---

## License

[Specify License Here - e.g., MIT]

---

## Contact & Support

- **GitHub Issues**: [Report bugs or feature requests](https://github.com/your-org/visuaLearn/issues)
- **Documentation**: See [specs/](./specs/001-interactive-viz/) folder
- **Developer Guide**: [specs/001-interactive-viz/quickstart.md](./specs/001-interactive-viz/quickstart.md)

---

## Acknowledgments

- **Google Gemini API** for AI-powered concept generation
- **React-Three-Fiber** for declarative 3D rendering
- **i18next** for multilingual support
- **Three.js community** for incredible 3D graphics library

---

**Last Updated**: 2025-11-24
**Maintained By**: [Your Team/Name]
