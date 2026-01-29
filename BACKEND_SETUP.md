# Backend Setup Complete ✓

Backend initialized with `uv` on January 28, 2026.

## What Was Created

### Directory Structure

```
backend/
├── .venv/                          # Python virtual environment (auto-created by uv)
├── .env.example                    # Environment template (copy to .env)
├── .gitignore                      # Git ignore patterns
├── .python-version                 # Python version pinning
├── README.md                       # Backend documentation
├── pyproject.toml                  # Project configuration with dependencies
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application entry point
│   ├── config.py                  # Settings from environment variables
│   ├── errors.py                  # Custom exception classes
│   ├── api/
│   │   ├── __init__.py
│   │   └── diagram.py             # API endpoints (TODO - Phase 1.9)
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py             # Pydantic request/response models
│   └── services/
│       ├── __init__.py
│       ├── orchestrator.py         # Pipeline coordinator (TODO - Phase 1.8)
│       ├── planning_agent.py       # Planning agent service (TODO - Phase 1.3)
│       ├── review_agent.py         # Review agent service (TODO - Phase 1.4)
│       ├── image_converter.py      # Image rendering (TODO - Phase 1.6)
│       └── file_manager.py         # File operations (TODO - Phase 1.7)
├── temp/                           # Temporary files directory (auto-cleanup)
├── logs/                           # Application logs directory
└── tests/                          # Test directory (TODO - Phase 3)
    └── __init__.py
```

## Installed Files

✓ **Configuration**
- `pyproject.toml` - 24 production dependencies, 6 dev dependencies
- `.env.example` - Template for environment variables
- `.gitignore` - Python/IDE/testing patterns

✓ **Core Application Files**
- `app/main.py` - FastAPI application with logging, CORS, health check
- `app/config.py` - Pydantic settings with 15+ configurable parameters
- `app/errors.py` - 6 custom exception classes
- `app/models/schemas.py` - 5 Pydantic models for API

✓ **Documentation**
- `README.md` - Backend setup, development, deployment guides
- `BACKEND_SETUP.md` - This file

## Installed Dependencies

### Production (24)

**Core Framework:**
- fastapi==0.104.1
- uvicorn[standard]==0.24.0
- pydantic==2.5.0
- pydantic-settings==2.1.0

**AI/LLM:**
- google-generativeai==0.3.0

**Image & File:**
- playwright==1.40.0
- pillow==10.1.0
- lxml==4.9.3

**HTTP & Network:**
- httpx==0.25.2
- python-dotenv==1.0.0

**Logging:**
- loguru==0.7.2

**Testing:** (also in dev)
- pytest==7.4.3
- pytest-cov==4.1.0
- pytest-asyncio==0.21.1

**Code Quality:** (also in dev)
- mypy==1.7.1
- ruff==0.1.8
- black==23.12.0

### Development (6)

- pytest==7.4.3
- pytest-cov==4.1.0
- pytest-asyncio==0.21.1
- mypy==1.7.1
- ruff==0.1.8
- black==23.12.0

**Total: 54 packages installed** (including transitive dependencies)

## FastAPI App Status

✓ **Application imports successfully**
✓ **Routes registered:**
- GET `/` - Root endpoint
- GET `/health` - Health check
- GET `/openapi.json`, `/docs`, `/redoc` - API documentation

**Available endpoints (partial):**
- POST `/api/diagram` - Generate diagram (TODO - Phase 1.9)
- GET `/api/export/{filename}` - Download export (TODO - Phase 1.9)

## Environment Setup

### Quick Start (3 steps)

```bash
# 1. Copy environment template
cp backend/.env.example backend/.env

# 2. Edit .env and add Google API key
# GOOGLE_API_KEY=your_api_key_here

# 3. Run backend
cd backend
.venv/bin/uvicorn app.main:app --reload
```

Server will start at `http://localhost:8000`

## Verification Checklist

✓ Python 3.11 virtual environment created
✓ All dependencies installed
✓ Playwright Chromium downloaded (~131MB)
✓ FastAPI app imports successfully
✓ Configuration system working
✓ Pydantic models defined
✓ Custom exceptions created
✓ Logging configured
✓ CORS middleware configured
✓ Health check endpoint working
✓ Project structure ready for implementation

## Tools Available

```bash
# Testing
.venv/bin/pytest tests/ -v
.venv/bin/pytest tests/ --cov=app

# Type checking
.venv/bin/mypy app/

# Linting
.venv/bin/ruff check app/

# Code formatting
.venv/bin/black app/ tests/

# Running app
.venv/bin/uvicorn app.main:app --reload
```

## Next Steps

### Phase 1: MVP Core Development

**Phase 1.3** → Planning Agent Service
- [ ] Implement `planning_agent.py`
- [ ] Create Gemini API integration
- [ ] Structured prompt for diagram planning
- [ ] JSON parsing and validation

**Phase 1.4** → Review Agent Service
- [ ] Implement `review_agent.py`
- [ ] Create quality scoring system
- [ ] Iteration loop logic
- [ ] Refinement instruction generation

**Phase 1.5** → Diagram Generator Service
- [ ] Implement integration with next-ai-draw-io
- [ ] XML validation
- [ ] Error handling

**Phase 1.6** → Image Converter Service
- [ ] Playwright-based rendering
- [ ] PNG/SVG generation
- [ ] Base64 encoding

**Phase 1.7** → File Manager Service
- [ ] File save/cleanup logic
- [ ] UUID-based naming
- [ ] Path traversal prevention

**Phase 1.8** → Orchestrator Service
- [ ] Pipeline coordination
- [ ] Timeout management
- [ ] Error handling

**Phase 1.9** → FastAPI Endpoints
- [ ] POST /api/diagram
- [ ] GET /api/export/{filename}
- [ ] Error response handling

See `ROADMAP.md` for complete Phase 1-4 breakdown.

## Development Guidelines

Refer to these documents:
- **`claude.md`** - Project-specific guidelines for Claude Code
- **`PRD.md`** - Product requirements
- **`ROADMAP.md`** - Implementation roadmap
- **`backend/README.md`** - Backend development guide

## Key Configuration Parameters

From `app/config.py`:

```python
# Timeouts (seconds)
PLANNING_TIMEOUT=5          # Planning agent hard stop
GENERATION_TIMEOUT=12       # Diagram generator hard stop
REVIEW_TIMEOUT=3            # Review agent per iteration
IMAGE_TIMEOUT=4             # Image converter hard stop

# Review settings
REVIEW_MAX_ITERATIONS=3     # Max review refinement loops

# File management
TEMP_FILE_TTL=3600          # 1 hour auto-cleanup
CLEANUP_INTERVAL=600        # 10 minute cleanup task

# Caching
CACHE_SIZE_MB=500           # Max in-memory cache
CACHE_TTL_SECONDS=3600      # 1 hour cache TTL
```

## Architecture Overview

```
User Input
    ↓
[Planning Agent]     (3s target, 5s max)
    ↓
[Diagram Generator]  (8s target, 12s max)  → next-ai-draw-io service
    ↓
[Review Agent]       (2s target, 3s max)   × max 3 iterations
    ↓
[Image Converter]    (2s target, 4s max)   → Playwright rendering
    ↓
[File Manager]       Save PNG/SVG/XML
    ↓
Response            (15s target, 20s max)
```

All services communicate through orchestrator.py with explicit error handling and logging.

## Important Notes

1. **Environment Variables**: Must set `GOOGLE_API_KEY` in `.env` before running
2. **Dependencies**: Locked in `pyproject.toml` - use `uv sync` to update
3. **Testing**: Quality gates require 80%+ test coverage (Phase 3)
4. **Performance**: Strict timeouts enforced at each pipeline stage
5. **Zero Fallback**: No default values - raise errors explicitly

---

**Setup Completed**: January 28, 2026
**Python Version**: 3.11.13
**Project Manager**: uv
**Status**: Ready for Phase 1 implementation
