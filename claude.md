# VisuaLearn Project Guidelines for Claude Code

## 1. Project Overview

**Project**: VisuaLearn - AI-Powered Educational Diagram Chatbot
**Status**: Pre-implementation (planning phase only)
**LLM Provider**: Google Gemini 2.5 Flash
**Repository**: Main branch (protected)

### Vision
Transform conceptual learning into visual understanding. Students input topics they want to learn, and the system generates high-quality educational diagrams with explanations—creating an intuitive, visual learning experience for ages 8-15.

### Success Criteria
- **Quality**: 90%+ diagram approval rate from review agent
- **Performance**: <15 seconds average generation time per diagram
- **Educational**: Accurate, age-appropriate content (8-15 years old)
- **Export Rate**: 60%+ of generated diagrams are exported by users

**Reference**: See PRD.md for full product requirements and SIMPLIFIED_FASTAPI_MVP.md for implementation baseline.

**Implementation Guide**: Follow ROADMAP.md strictly - it contains all Phase-by-Phase tasks with clear acceptance criteria. Backend is initialized in `/backend` with uv. See BACKEND_SETUP.md for status.

---

## 2. Development Workflow (Phase-by-Phase with Testing)

### Overall Development Process

```
ROADMAP.md (Follow Strictly)
    ↓
Phase 1: Develop ALL code for phase
    ├─ Phase 1.1: Backend Infrastructure
    ├─ Phase 1.2: Pydantic Models
    ├─ ... (complete ALL tasks)
    ├─ Phase 1.11: Integration Testing
    ↓
Phase 1: Test ALL code for phase
    ├─ Create test files matching implemented features
    ├─ Write comprehensive test cases
    ├─ Run tests: pytest tests/ --cov=app
    ├─ Run quality gates: mypy, ruff, black
    ├─ Fix issues until 80%+ coverage and all tests pass
    ↓
Phase 1 Complete: Verify against ROADMAP.md
    ├─ Check all acceptance criteria met
    ├─ Verify end-to-end functionality
    ├─ Commit all code and tests
    ↓
Phase 2: Repeat (Develop → Test → Verify)
```

### Phase-by-Phase Workflow

**For each phase, follow this sequence**:

#### Step 1: Develop All Code

1. Read ROADMAP.md for phase requirements
2. Implement **all tasks** in the phase (Phase 1.1 through 1.11)
3. Create all necessary files (services, models, endpoints)
4. Write code following architecture guidelines
5. **Do NOT write tests yet** - focus on implementation

**Example Phase 1 Code Tasks**:
- Phase 1.1: Backend Infrastructure ✓ (already done)
- Phase 1.2: Pydantic Models & Errors ✓ (already done)
- Phase 1.3: Planning Agent Service
- Phase 1.4: Review Agent Service
- Phase 1.5: Diagram Generator Integration
- Phase 1.6: Image Converter Service
- Phase 1.7: File Manager Service
- Phase 1.8: Orchestrator Service
- Phase 1.9: FastAPI Endpoints
- Phase 1.10: Frontend Setup
- Phase 1.11: Integration Testing

#### Step 2: Create Tests

After all code for phase is complete:

1. Create test files in `/backend/tests/` matching app structure
2. Write comprehensive test cases for each module
3. Test organization:

```
tests/
├── __init__.py
├── conftest.py                      # Shared fixtures and mocks
├── test_models.py                   # Pydantic models validation
├── test_config.py                   # Configuration loading
├── test_errors.py                   # Error handling
├── services/
│   ├── test_planning_agent.py       # Planning agent tests
│   ├── test_review_agent.py         # Review agent tests
│   ├── test_image_converter.py      # Image converter tests
│   ├── test_file_manager.py         # File manager tests
│   └── test_orchestrator.py         # Orchestrator pipeline tests
└── api/
    └── test_diagram.py              # API endpoint tests
```

#### Step 3: Run Tests

```bash
# Run all tests with coverage report
cd backend
.venv/bin/pytest tests/ --cov=app --cov-report=term-missing -v

# Expected result: 80%+ coverage, all tests passing
```

#### Step 4: Quality Gates

```bash
# Type checking
.venv/bin/mypy app/ --strict

# Linting
.venv/bin/ruff check app/ tests/

# Code formatting
.venv/bin/black --check app/ tests/
```

If any checks fail, fix code and re-run tests.

#### Step 5: Verify Against ROADMAP

1. Check ROADMAP.md for phase acceptance criteria
2. Verify each acceptance criterion is met
3. Test end-to-end functionality manually if applicable

#### Step 6: Commit

Only after tests pass and quality gates clean:

```bash
git add app/ tests/
git commit -m "Phase 1: Implement backend services with tests

Phase 1 Implementation:
- 1.3: Planning Agent Service with Gemini integration
- 1.4: Review Agent with quality scoring
- 1.5: Diagram Generator integration with next-ai-draw-io
- 1.6: Image Converter using Playwright
- 1.7: File Manager with auto-cleanup
- 1.8: Orchestrator pipeline coordinator
- 1.9: FastAPI endpoints (diagram, export)

Testing:
- 45+ test cases covering all services
- 85% code coverage
- All tests passing
- Type checking and linting clean
- Quality gates passing"
```

### Test File Pattern

Each test file should follow this structure:

```python
# tests/services/test_planning_agent.py
"""Tests for PlanningAgent service."""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock

from app.services.planning_agent import PlanningAgent
from app.errors import PlanningError


class TestPlanningAgent:
    """Planning agent tests."""

    def test_init(self):
        """Test agent initialization."""
        agent = PlanningAgent()
        assert agent is not None
        assert agent.timeout == 5

    @pytest.mark.asyncio
    async def test_analyze_valid_input(self):
        """Test successful planning analysis."""
        agent = PlanningAgent()
        result = await agent.analyze("Explain photosynthesis")

        # Verify response structure
        assert result.concept is not None
        assert result.diagram_type in ["flowchart", "mindmap", "sequence", "hierarchy"]
        assert len(result.components) > 0

    @pytest.mark.asyncio
    async def test_analyze_empty_input(self):
        """Test error handling for empty input."""
        agent = PlanningAgent()
        with pytest.raises(PlanningError):
            await agent.analyze("")

    @pytest.mark.asyncio
    async def test_analyze_long_input(self):
        """Test error handling for input exceeding max length."""
        agent = PlanningAgent()
        with pytest.raises(PlanningError):
            await agent.analyze("x" * 1001)

    @pytest.mark.asyncio
    async def test_analyze_timeout(self, mocker):
        """Test timeout handling."""
        agent = PlanningAgent()
        # Mock the Gemini API call to timeout
        mocker.patch.object(
            agent,
            '_call_gemini',
            side_effect=asyncio.TimeoutError()
        )

        with pytest.raises(PlanningError, match="timed out"):
            await agent.analyze("topic")

    @pytest.mark.asyncio
    async def test_analyze_api_error(self, mocker):
        """Test API error handling."""
        agent = PlanningAgent()
        mocker.patch.object(
            agent,
            '_call_gemini',
            side_effect=Exception("API error")
        )

        with pytest.raises(PlanningError):
            await agent.analyze("topic")
```

### Running Tests During Development

```bash
# Run tests for specific module
.venv/bin/pytest tests/services/test_planning_agent.py -v

# Run with coverage and show uncovered lines
.venv/bin/pytest tests/ --cov=app --cov-report=term-missing

# Run in watch mode (auto-run on file changes)
.venv/bin/pytest-watch tests/ -v

# Run specific test
.venv/bin/pytest tests/services/test_planning_agent.py::TestPlanningAgent::test_analyze_valid_input -v
```

### Checklist for Completing Each Phase

- [ ] All code tasks (1.1-1.11 for Phase 1) implemented
- [ ] All services functional and integrated
- [ ] Test files created for all modules
- [ ] All tests written and passing
- [ ] 80%+ code coverage achieved
- [ ] Type checking passes (`mypy app/`)
- [ ] Linting passes (`ruff check app/`)
- [ ] Formatting correct (`black --check app/`)
- [ ] All acceptance criteria from ROADMAP.md met
- [ ] End-to-end functionality verified
- [ ] Code committed with comprehensive message
- [ ] Ready for next phase

---

## 3. Architecture Principles

### Core Design Philosophy
- **Stateless-First**: No database, session-based only. All state lives in memory during request.
- **Sequential Pipeline**: Planning → Generation → Review → Conversion. Each stage has clear timeouts.
- **Quality Over Speed**: Review agent must approve diagram before presenting to user.
- **Educational Focus**: All content must be age-appropriate, pedagogically sound, and accurate.
- **Zero Fallback Policy**: No default values, no silent failures. Raise explicit errors through user-facing toasts.
- **API-First Design**: Clear separation between frontend (React) and backend (FastAPI).

### Agent Pipeline Architecture
```
User Input
    ↓
Planning Agent (3s target, 5s max)
    ├─ Concept analysis
    ├─ Diagram type selection
    ├─ Component identification
    └─ Success criteria definition
    ↓
Diagram Generator → next-ai-draw-io (8s target, 12s max)
    ├─ XML generation via Gemini
    ├─ Sends planning to draw.io service
    └─ Returns valid draw.io XML
    ↓
Review Agent (2s target, 3s max per iteration, max 3 iterations)
    ├─ XML parsing and validation
    ├─ Comparison against plan
    ├─ Quality scoring (0-100)
    └─ Refinement instructions if needed
    ↓
Image Converter (2s target, 4s max)
    ├─ XML → PNG (Playwright)
    └─ PNG → Base64 (inline display) + File storage (export)
    ↓
Response to User (Total: 15s target, 20s absolute max)
```

---

## 3. Technology Stack & Dependencies

### Backend
- **Runtime**: Python 3.11+
- **Framework**: FastAPI + Uvicorn
- **LLM Integration**: `google-generativeai` SDK (Gemini 2.5 Flash)
- **Image Rendering**: Playwright (Chromium)
- **Validation**: Pydantic v2
- **Logging**: Loguru
- **Async HTTP**: httpx
- **File Operations**: Standard library (pathlib, tempfile)

### Frontend
- **Framework**: React 18 + Vite
- **Language**: TypeScript
- **Styling**: Tailwind CSS + shadcn/ui
- **State**: React useState/useReducer (session only, no persistence)
- **HTTP Client**: Axios with streaming support

### External Services
- **next-ai-draw-io**: Node.js service (port 3001)
  - Configuration: `AI_PROVIDER=gemini`
  - Docker image: `ghcr.io/dayuanjiang/next-ai-draw-io:latest`
  - Receives XML generation requests, returns valid draw.io XML
- **Google Gemini 2.5 Flash API**:
  - Access: Google AI Studio (development) or Vertex AI (production)
  - Three uses: Planning agent, Review agent, Diagram generation via next-ai-draw-io
  - Alternative: Gemini 2.0 Flash-Lite for cost optimization

### File Storage
- **Temporary**: `/backend/temp` directory with UUID-based filenames
- **Auto-cleanup**: 1 hour TTL with background cleanup task
- **Security**: Path traversal prevention, extension validation (PNG, SVG, XML only)
- **Size Limits**: Max 5MB per file

---

## 4. Agent Workflow & Coordination

### Planning Agent (Gemini 2.5 Flash)
**Goal**: Understand the educational concept deeply and create diagram specifications.

**Inputs**:
- User question (raw text)
- Language preference (en | zh)

**Outputs**:
```json
{
  "concept": "string (the core concept being explained)",
  "diagram_type": "flowchart | mindmap | sequence | hierarchy",
  "components": ["list of diagram elements"],
  "relationships": [
    {"from": "component1", "to": "component2", "label": "relationship"}
  ],
  "success_criteria": ["measurable criteria for validation"],
  "educational_level": "8-10 | 11-13 | 14-15",
  "key_insights": ["important teaching points"]
}
```

**Timeout**: 5 seconds (hard stop)
**Target**: 3 seconds

**Implementation Notes**:
- Use structured prompts with clear JSON output format
- Validate JSON parsing immediately
- Include curriculum alignment guidance for Hong Kong Education Bureau standards
- Never return partial/malformed JSON—raise error if parsing fails

### Diagram Generator (next-ai-draw-io Service)
**Goal**: Convert planning agent output into valid draw.io XML.

**Input**: Planning output + refinement instructions (if iterating)

**Output**: Valid draw.io XML that can be imported and rendered

**Timeout**: 12 seconds (hard stop)
**Target**: 8 seconds

**Implementation Notes**:
- Call next-ai-draw-io REST API with planning JSON
- Service handles Gemini integration internally (configured with AI_PROVIDER=gemini)
- Validate XML structure immediately using lxml
- Ensure XML is importable into draw.io without errors
- If XML validation fails, don't try to fix—return error for review agent refinement

### Review Agent (Gemini 2.5 Flash)
**Goal**: Validate diagram quality and approve for presentation to user.

**Inputs**:
- Generated XML
- Original planning specs
- Current iteration count

**Outputs**:
```json
{
  "score": 0-100,
  "approved": true | false,
  "issues": ["list of identified issues"],
  "refinement_instructions": "string with specific improvements needed",
  "educational_alignment": "Assessment of pedagogical quality"
}
```

**Timeout**: 3 seconds per iteration (hard stop)
**Target**: 2 seconds per iteration
**Max Iterations**: 3 (hard stop—accept score 70+ on iteration 3)

**Approval Threshold**:
- Score ≥90: Approve immediately
- Score 70-89: Refine once, re-review
- Score <70 on iteration 3: Accept anyway (don't reject to user)

**Implementation Notes**:
- Parse XML to extract actual structure
- Compare against original plan (component presence, relationships, labels)
- Provide specific, actionable refinement instructions
- Never silently degrade—always communicate issues to user via metadata

### Image Converter (Playwright)
**Goal**: Render XML to PNG and prepare for display/export.

**Inputs**: Valid draw.io XML

**Outputs**:
- PNG file (1200px width for display, 2400px for high-res export)
- Base64-encoded PNG (for inline display in chat)
- SVG version (for vector export)
- Original XML (for download/editing)

**Timeout**: 4 seconds (hard stop)
**Target**: 2 seconds

**Performance Optimization**:
- Preload Playwright browser instance on backend startup
- Reuse browser across requests (connection pooling)
- Render PNG + SVG in parallel
- Cache identical render requests in-memory (session-based)

**Implementation Notes**:
- Use Playwright to load draw.io XML and render to image
- Ensure text is readable on mobile devices (min 12px font)
- Optimize file size (<500KB) with appropriate compression
- Save to `/backend/temp` with auto-cleanup timer

---

## 5. API Design Patterns

### POST /api/diagram
**Purpose**: Generate diagram from concept

**Request**:
```json
{
  "user_input": "string (1-1000 chars, required)",
  "language": "en | zh (default: en)"
}
```

**Response** (200 OK):
```json
{
  "explanation": "string (streaming explanation text)",
  "diagram_image": "data:image/png;base64,... (inline display)",
  "diagram_xml": "<mxfile>...</mxfile> (raw XML)",
  "export_urls": {
    "png": "/api/export/temp_abc123.png",
    "svg": "/api/export/temp_abc123.svg",
    "xml": "/api/export/temp_abc123.xml"
  },
  "metadata": {
    "iterations": 2,
    "approved": true,
    "score": 92.5,
    "generation_time": 12.3,
    "planning_time": 2.1,
    "review_iterations": 2
  }
}
```

**Error Response** (400/500):
```json
{
  "error": "specific error type",
  "message": "user-friendly error message",
  "details": "technical details for debugging"
}
```

**Implementation Notes**:
- Stream explanation text to frontend while diagram generates in background
- Use Pydantic v2 for strict validation
- All fields required (no null values, no fallbacks)
- Raise specific errors: `InputValidationError`, `PlanningError`, `GenerationError`, `ReviewError`, `RenderingError`
- Never return partial responses

### GET /api/export/{filename}
**Purpose**: Download exported diagram files

**Response** (200 OK):
- Content-Type: image/png | image/svg+xml | application/xml
- Content-Disposition: attachment; filename="..."
- File binary data

**Error Response** (404):
- File not found (auto-deleted after 1 hour)

**Implementation Notes**:
- Validate filename format (UUID-based, safe characters only)
- Prevent path traversal with strict validation
- Check file exists and extension is allowed (png, svg, xml)
- Set auto-delete timer on file access

### Error Handling Philosophy
**Zero Fallback Policy**: Never use default values or silent failures.

When something goes wrong:
1. **Identify the specific error** (validation, timeout, API failure, etc.)
2. **Create a clear error message** that users can understand
3. **Provide actionable guidance** (e.g., "Try a simpler question", "Rephrase your input")
4. **Log full technical details** for debugging
5. **Return structured error response** to frontend for toast display

**Never**:
- ❌ Return partial/incomplete responses
- ❌ Use default values or fallback data
- ❌ Silently skip validation steps
- ❌ Ignore API timeouts
- ❌ Return null for required fields

---

## 6. Quality Standards for Educational Content

### Age-Appropriateness (8-15 years)
- **Language Level**: Simple, clear explanations without jargon
- **Content Complexity**: Age-appropriate (8-10 simple, 11-13 intermediate, 14-15 advanced)
- **Tone**: Encouraging, positive, educational
- **Topics**: Science, math, technology, history (no violence, adult themes, inappropriate content)

### Pedagogical Quality Criteria
- **Accuracy**: Scientifically/mathematically correct
- **Clarity**: Visual hierarchy clear, relationships explicit
- **Completeness**: All key components present, no missing elements
- **Accessibility**: Labels readable, colors have sufficient contrast
- **Age Alignment**: Complexity matches student level

### Review Agent Scoring (0-100 scale)
- **90+**: Excellent. Ready to show user. Core concept well-explained, all components present, age-appropriate.
- **70-89**: Good. Minor issues. Missing non-critical elements, could improve clarity, but core concept intact.
- **Below 70**: Poor. Significant issues. Missing components, inaccurate information, or age-inappropriate content.

**Approval Logic**:
- Iteration 1-2: Must score ≥90 to approve
- Iteration 3: Accept any diagram (don't reject to user)

### AI-Generated Content Disclaimer
Every response must include: "⚠️ This diagram is AI-generated. Please verify with your teacher or textbook for accuracy."

### Content Filtering
Block generation for:
- Violent or graphic content
- Adult/explicit material
- Spam or nonsensical requests
- Harmful instructions
- Personal identifying information (PII)

**Implementation**: Add content filter check in planning agent before proceeding.

---

## 7. File Management & Temporary Storage

### Directory Structure
```
/backend/temp/
├── [uuid].png        (display image)
├── [uuid].svg        (vector export)
├── [uuid].xml        (editable diagram)
└── .cleanup          (tracking file for auto-cleanup)
```

### Lifecycle
1. **Creation**: Generate with UUID filename during request
2. **Storage**: Save to `/backend/temp` directory
3. **Access**: Provide export URLs in response
4. **Cleanup**: Auto-delete after 1 hour
   - Background task runs every 10 minutes
   - Deletes files older than 1 hour
   - Log deletion events

### Security Rules
- **Path Traversal Prevention**: Validate all filenames strictly
  - Allow only: `[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\.(png|svg|xml)`
  - Reject any path containing `..`, `/`, `\`
- **Extension Validation**: Only PNG, SVG, XML allowed
- **Size Limits**: Max 5MB per file
- **Atomic Operations**: Use tempfile library for atomic writes

### File Naming Convention
```
{uuid}.{extension}
Example: 550e8400-e29b-41d4-a716-446655440000.png
```

---

## 8. Performance Optimization Rules

### Timeout Strategy
All external API calls must have explicit timeouts:
- **Planning Agent (Gemini)**: 5s hard timeout
- **Diagram Generator (next-ai-draw-io)**: 12s hard timeout
- **Review Agent (Gemini)**: 3s per iteration hard timeout
- **Image Converter (Playwright)**: 4s hard timeout
- **File Operations**: 1s hard timeout

**Implementation**: Use `asyncio.timeout()` or `httpx.timeout()` for all calls.

### Concurrency & Parallelization
- Use `asyncio` for all I/O operations
- Image conversion (PNG + SVG) run in parallel
- Cache Gemini responses for identical queries (in-memory, session-based)
- Stream explanation text to frontend while diagram generates
- Never block async event loop with synchronous operations

### Resource Management
- **Playwright Browser**: Preload on startup, reuse across requests
- **Gemini API**: Implement request queuing if needed (max 100 concurrent)
- **Memory**: Store in-memory cache max 500MB (clear on eviction)
- **Disk**: Monitor `/backend/temp` size, alert if >1GB

### Optimization Targets
- Planning Agent: 3s (5s max)
- Diagram Generator: 8s (12s max)
- Review Agent: 2s per iteration (3s max)
- Image Converter: 2s (4s max)
- Total End-to-End: 15s (20s absolute max)
- P95 Latency: <15s (monitor continuously)

### XML Complexity Limits
To prevent performance degradation:
- Max nodes: 50
- Max edges: 100
- Max text length per node: 200 chars
- Max nesting depth: 5

**Implementation**: Validate in review agent; if exceeded, request simplified planning.

### Caching Strategy
- **Query Cache**: Store Gemini responses for identical inputs (1-hour TTL)
- **Component Cache**: Store commonly used diagram templates
- **Image Cache**: Cache identical rendered outputs
- **Session-Based**: Clear cache when user closes browser

---

## 9. Testing Strategy

### Unit Tests (pytest)
**Target**: 80% coverage

**Coverage Areas**:
- Pydantic model validation
- Planning agent output parsing
- XML parsing and validation
- Error handling and edge cases
- Utility functions (file ops, formatting, etc.)

**Example**:
```python
def test_diagram_request_validation():
    # Valid request
    req = DiagramRequest(user_input="Explain photosynthesis", language="en")
    assert req.user_input == "Explain photosynthesis"

    # Invalid: empty input
    with pytest.raises(ValidationError):
        DiagramRequest(user_input="", language="en")

    # Invalid: too long
    with pytest.raises(ValidationError):
        DiagramRequest(user_input="x" * 1001, language="en")
```

### Integration Tests
- Test full pipeline with real API calls (mocked for Gemini)
- Test next-ai-draw-io integration
- Test Playwright rendering
- Test file cleanup
- Test error scenarios (timeouts, invalid XML, etc.)

### E2E Tests (Playwright)
- User flow: Input → Explanation → Diagram → Export
- Error scenarios: Invalid input, timeout, generation failure
- Mobile responsiveness
- Accessibility (keyboard navigation, screen reader)

### Quality Gates (Required Before Commit)
```bash
# 1. Run all tests
pytest tests/ --cov=app --cov-report=term-missing

# 2. Type checking
mypy app/

# 3. Linting
ruff check app/

# 4. Formatting
black --check app/

# 5. Performance benchmark
pytest tests/benchmarks/ --benchmark-only
```

**Acceptance Criteria**:
- All tests pass
- Coverage ≥80%
- No type errors
- P95 latency <15s

---

## 10. Common Pitfalls & Anti-Patterns

### ❌ Anti-Patterns to Avoid

**1. Using Fallback Values**
```python
# BAD
score = review_data.get('score', 85)  # Silent default!

# GOOD
if 'score' not in review_data:
    raise ReviewError("Score missing from review response")
score = review_data['score']
```

**2. Silent Failures**
```python
# BAD
try:
    xml = generate_xml(plan)
except Exception as e:
    logger.error(str(e))  # Silent failure!
    return None  # This will break downstream

# GOOD
try:
    xml = generate_xml(plan)
except XmlGenerationError as e:
    logger.error(f"XML generation failed: {e}")
    raise GenerationError(f"Could not create diagram: {e.message}")
```

**3. Blocking I/O in Async Context**
```python
# BAD
def generate_diagram():
    time.sleep(2)  # BLOCKS EVENT LOOP!

# GOOD
async def generate_diagram():
    await asyncio.sleep(2)  # Non-blocking
```

**4. Hardcoded Configuration**
```python
# BAD
GEMINI_API_KEY = "sk-1234..."
DRAWIO_URL = "http://localhost:3001"

# GOOD
from pydantic_settings import BaseSettings
class Settings(BaseSettings):
    gemini_api_key: str  # From environment
    drawio_url: str      # From environment
```

**5. Missing Timeouts**
```python
# BAD
response = httpx.get("http://external-api.com")  # No timeout!

# GOOD
response = httpx.get("http://external-api.com", timeout=5.0)
```

**6. Ignored Validation Errors**
```python
# BAD
try:
    request = DiagramRequest(**data)
except ValidationError:
    pass  # Silently ignore!

# GOOD
try:
    request = DiagramRequest(**data)
except ValidationError as e:
    raise InputValidationError(f"Invalid request: {e.errors()}")
```

### ✅ Best Practices

**1. Explicit Error Handling**
```python
# Define custom exceptions
class VisuaLearnError(Exception):
    """Base error for VisuaLearn"""
    pass

class PlanningError(VisuaLearnError):
    """Planning agent failed"""
    pass

class ReviewError(VisuaLearnError):
    """Review agent failed"""
    pass

# Use them
try:
    plan = await planning_agent.analyze(user_input)
except Exception as e:
    raise PlanningError(f"Failed to plan diagram: {e}")
```

**2. Structured Logging**
```python
from loguru import logger

logger.info(
    "Diagram generated",
    user_input=user_input,
    diagram_type=plan.diagram_type,
    iterations=iterations,
    score=score,
    generation_time=elapsed
)
```

**3. Timeout Patterns**
```python
import asyncio

try:
    async with asyncio.timeout(5.0):
        result = await planning_agent.analyze(user_input)
except asyncio.TimeoutError:
    raise PlanningError("Planning agent timed out (5s)")
```

**4. Validation First**
```python
# Always validate before processing
try:
    request = DiagramRequest(**payload)
except ValidationError as e:
    raise InputValidationError(f"Invalid input: {e.json()}")

# Then proceed safely
plan = await planning_agent.analyze(request.user_input)
```

---

## 11. Development Workflow

### Local Setup
```bash
# 1. Clone and install
git clone [repo]
cd visuaLearn

# 2. Backend dependencies
cd backend
pip install -r requirements.txt
playwright install chromium

# 3. Frontend dependencies
cd ../frontend
npm install

# 4. Environment setup
cp .env.example .env
# Edit .env with your Google API key
```

### Feature Implementation Process
1. **Plan**: Discuss approach, update tasks
2. **Branch**: Create feature branch from main
3. **Implement**: Write code following guidelines
4. **Test**: Run full test suite, achieve 80%+ coverage
5. **Review**: Self-review against quality gates
6. **Commit**: Create meaningful commit message
7. **PR**: Submit PR for review before merging to main

### Git Workflow
```bash
# Create feature branch
git checkout -b feature/[name]

# Make changes, commit regularly
git commit -m "description"

# Before pushing: ensure tests pass
pytest tests/ --cov=app

# Push and create PR
git push origin feature/[name]
```

### Code Review Checklist
- [ ] Tests pass (pytest)
- [ ] Type checking passes (mypy)
- [ ] Linting passes (ruff)
- [ ] Formatting correct (black)
- [ ] No hardcoded configuration
- [ ] Timeouts on all external calls
- [ ] Error handling is explicit (no fallbacks)
- [ ] Documentation updated if needed
- [ ] Performance targets met (<15s p95)

### Running Tests Before Commits
```bash
# Full test suite
pytest tests/ --cov=app --cov-report=term-missing

# Specific test file
pytest tests/test_planning_agent.py -v

# Watch mode (auto-run on file change)
pytest-watch tests/

# With profiling
pytest tests/ --profile
```

---

## 12. Persona Guidance for Claude Code

### Recommended Personas by Task Type

**Architecture & Planning** → `--persona-architect`
- System design decisions
- Integration planning
- Scalability considerations
- MCP: Sequential, Context7

**Backend Implementation** → `--persona-backend`
- API design
- Service implementation
- Error handling
- MCP: Context7, Sequential

**Frontend Implementation** → `--persona-frontend`
- React components
- User experience
- Mobile responsiveness
- Accessibility compliance
- MCP: Magic, Playwright

**Bug Investigation** → `--persona-analyzer`
- Root cause analysis
- Systematic debugging
- Evidence collection
- MCP: Sequential, Grep, Read

**Code Quality** → `--persona-refactorer`
- Code simplification
- Technical debt reduction
- Pattern consistency
- MCP: Sequential, Context7

**Testing & Validation** → `--persona-qa`
- Test strategy
- Coverage analysis
- Edge case identification
- MCP: Playwright, Sequential

### Command Recommendations

| Task | Command | Flags |
|------|---------|-------|
| Architecture review | `/analyze --scope project` | `--persona-architect --think-hard` |
| API endpoint implementation | `/implement` | `--persona-backend --c7` |
| Component creation | `/implement` | `--persona-frontend --magic` |
| Bug fix | `/troubleshoot` | `--persona-analyzer --think` |
| Test writing | `/test` | `--persona-qa --play` |
| Refactoring | `/improve --quality` | `--persona-refactorer --seq` |
| Documentation | `/document` | `--persona-scribe=en` |
| Performance optimization | `/improve --perf` | `--persona-performance --think` |

### MCP Server Integration
- **Context7**: Library patterns, FastAPI docs, Pydantic validation, draw.io specs
- **Sequential**: Complex analysis, multi-step planning, architectural decisions
- **Magic**: React components, UI layouts, Tailwind patterns
- **Playwright**: E2E test generation, performance validation, mobile testing

---

## 13. Environment Variables & Configuration

### Required Variables
```env
# Google Gemini API
GOOGLE_API_KEY=your_google_api_key_here

# External Services
DRAWIO_SERVICE_URL=http://localhost:3001

# Python Settings
DEBUG=true
LOG_LEVEL=INFO
```

### Optional Variables
```env
# Performance Tuning
PLANNING_TIMEOUT=5
GENERATION_TIMEOUT=12
REVIEW_TIMEOUT=3
IMAGE_TIMEOUT=4
REVIEW_MAX_ITERATIONS=3

# File Management
TEMP_DIR=./backend/temp
TEMP_FILE_TTL=3600
CLEANUP_INTERVAL=600

# Caching
CACHE_SIZE_MB=500
CACHE_TTL_SECONDS=3600

# Server
HOST=0.0.0.0
PORT=8000
WORKERS=4
```

### Configuration Management
```python
# app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    google_api_key: str
    drawio_service_url: str
    debug: bool = False
    log_level: str = "INFO"
    planning_timeout: int = 5
    generation_timeout: int = 12
    review_timeout: int = 3
    image_timeout: int = 4
    review_max_iterations: int = 3

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
```

### Local Development (.env.example)
```env
# Copy to .env and fill in your values
GOOGLE_API_KEY=
DRAWIO_SERVICE_URL=http://localhost:3001
DEBUG=true
LOG_LEVEL=DEBUG
```

### Pre-Commit Safety
- **Never commit** `.env` files
- **Never commit** API keys or secrets
- **Always use** environment variables from `.env.example`
- **Validate** that secrets aren't in git history: `git log -p | grep -i 'api_key'`

---

## 14. Logging & Debugging

### Structured Logging with Loguru
```python
from loguru import logger

# Configuration
logger.remove()  # Remove default handler
logger.add(
    sys.stderr,
    format="<level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level="DEBUG"
)
logger.add(
    "logs/diagram_{time}.log",
    rotation="500 MB",
    retention="7 days",
    level="DEBUG"
)
```

### Log Levels & Usage

**DEBUG**: Development details
```python
logger.debug(f"Planning input: {user_input}")
logger.debug(f"Parsing XML structure: {xml[:100]}...")
```

**INFO**: Important operational events
```python
logger.info(
    "Diagram generated successfully",
    iterations=2,
    score=92.5,
    generation_time=12.3
)
```

**WARNING**: Recoverable issues
```python
logger.warning(f"Review iteration {iteration} scored below 90: {score}")
logger.warning(f"File cleanup skipped for {filename} (still in use)")
```

**ERROR**: Non-fatal errors (still return response)
```python
logger.error(f"Image rendering took {elapsed}s (target 2s)")
logger.error(f"Gemini API rate limit, queuing request")
```

**CRITICAL**: Fatal errors (abort request)
```python
logger.critical(f"Planning agent failed: {error}")
raise PlanningError(str(error))
```

### Key Metrics to Track

**Performance**:
- `planning_time`: Time for planning agent (target 3s)
- `generation_time`: Time for diagram generator (target 8s)
- `review_time`: Time for review agent (target 2s per iteration)
- `image_time`: Time for image conversion (target 2s)
- `total_time`: End-to-end time (target 15s)

**Quality**:
- `review_score`: Final approval score (0-100)
- `review_iterations`: Number of refinement iterations (1-3)
- `approved`: Whether diagram was approved
- `issues_found`: Number of quality issues identified

**Usage**:
- `user_input`: What the student asked
- `language`: Input language (en | zh)
- `diagram_type`: Type selected (flowchart | mindmap | etc)
- `export_count`: Number of formats exported

### Example Logging
```python
async def generate_diagram(request: DiagramRequest):
    start_time = time.time()

    # Log input
    logger.info("Received diagram request", user_input=request.user_input)

    # Planning
    planning_start = time.time()
    plan = await planning_agent.analyze(request.user_input)
    planning_time = time.time() - planning_start
    logger.info(f"Planning completed", diagram_type=plan.diagram_type, time=planning_time)

    # ... continue logging each stage ...

    # Final log
    total_time = time.time() - start_time
    logger.info(
        "Diagram generation complete",
        total_time=total_time,
        iterations=review_iterations,
        score=final_score,
        approved=approved
    )
```

### Debugging Workflow

**Problem**: "Diagram generation timing out"
1. Check logs: Filter by `generation_timeout`
2. Identify stage: Is it planning, generation, review, or image conversion?
3. Add debug logs: `logger.debug()` in that stage
4. Profile: Use `asyncio.timeout()` to find bottleneck
5. Optimize: Cache, parallelize, or simplify

**Problem**: "Review agent keeps rejecting diagrams"
1. Log review output: `logger.debug(f"Review response: {review_data}")`
2. Check XML: `logger.debug(f"Generated XML: {xml[:500]}")`
3. Compare plan vs XML: Are all components present?
4. Adjust prompt: Make planning agent more specific

---

## 15. Deployment Considerations

### Pre-Deployment Checklist
- [ ] All tests pass (80%+ coverage)
- [ ] No hardcoded configuration
- [ ] All secrets in environment variables
- [ ] API keys rotated/verified
- [ ] Performance benchmarks <15s
- [ ] Error handling covers all paths
- [ ] Logging configured correctly
- [ ] Cleanup tasks tested
- [ ] File permissions set correctly
- [ ] Documentation updated
- [ ] Rate limiting implemented (if needed)
- [ ] Monitoring/alerting configured

### Infrastructure Recommendations

**Frontend Hosting**:
- **Vercel** (recommended): Automatic deployments from git, edge functions, analytics
- **Netlify**: Similar to Vercel, good for React/Vite
- **AWS S3 + CloudFront**: For cost-sensitive deployments

**Backend Hosting**:
- **Railway**: Simple Python hosting, good for MVP
- **Render**: Similar to Railway, good DX
- **AWS EC2**: Full control, more complex setup
- **Google Cloud Run**: Serverless Python, pay per use

**next-ai-draw-io Service**:
- **Docker**: Run as containerized service
- **GCP Cloud Run**: Serverless option (good for cost)
- **AWS ECS**: Managed container orchestration
- **Self-hosted**: Run on same server as backend

**Database** (Not needed for MVP):
- Stateless design means no database required
- Optional: S3/R2 for long-term export storage

### Scalability Planning

**Bottleneck 1: Gemini API Rate Limits**
- Implement request queuing (max 100 concurrent)
- Implement exponential backoff for retries
- Monitor API usage, set up alerting

**Bottleneck 2: Playwright Browser Rendering**
- Preload browser instance (don't create/destroy per request)
- Use browser pool for concurrent renders
- Implement image caching

**Bottleneck 3: File Storage**
- Clean up temp files aggressively (1-hour TTL)
- Monitor disk usage, alert if >80%
- Consider S3/R2 for production exports

### Health Checks
Implement `/health` endpoint that checks:
- Gemini API connectivity
- next-ai-draw-io service connectivity
- Playwright browser status
- Disk space availability
- Memory usage

```python
@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "gemini": await check_gemini(),
        "drawio": await check_drawio(),
        "playwright": await check_playwright(),
        "disk_usage_percent": get_disk_usage()
    }
```

### Monitoring & Alerting
Key metrics to monitor:
- **Availability**: Uptime % (target 99.5%)
- **Performance**: P95 latency (target <15s)
- **Error Rate**: % of failed requests (target <0.5%)
- **Resource Usage**: Memory, CPU, disk (alert if >80%)
- **API Usage**: Gemini API calls/cost (budget alerts)

### Rollback Strategy
- Maintain previous version on standby
- Use feature flags to disable problematic features
- Database-free design means simple rollback (no migration issues)
- Keep detailed logs for troubleshooting

---

## Summary

This document provides comprehensive project-specific guidance for VisuaLearn development with Claude Code. Key principles:

1. **Stateless architecture** with session-based generation only
2. **Zero fallback policy** - raise errors, never use defaults
3. **Sequential pipeline** with explicit timeouts at each stage
4. **Quality over speed** - review agent approval required
5. **Google Gemini 2.5 Flash** as the LLM provider
6. **Age-appropriate education** content (8-15 years)
7. **Performance targets** of <15s end-to-end

For detailed specifications, see:
- **PRD.md**: Full product requirements
- **SIMPLIFIED_FASTAPI_MVP.md**: Implementation baseline
- **Test specs**: Will be in `/backend/tests/` once implementation starts

---

**Document Version**: 1.0
**Last Updated**: January 28, 2026
**Maintained By**: Development Team
