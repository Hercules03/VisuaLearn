# VisuaLearn Development Guide

**Last Updated**: January 28, 2026
**Status**: Backend initialized, ready for Phase 1 implementation

---

## Overview

This guide explains how to develop VisuaLearn following the **phase-by-phase workflow** with comprehensive testing. The project is managed through ROADMAP.md and implemented according to claude.md guidelines.

---

## Development Workflow

### The Cycle: Develop → Test → Verify

```
┌─────────────────────────────────────────────────┐
│                  ROADMAP.md                     │
│          Phase-by-Phase Task List               │
└─────────────┬───────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────┐
│           PHASE 1: DEVELOP ALL CODE             │
│  Implement all tasks (1.1 - 1.11) completely   │
│  - No tests yet                                 │
│  - Focus on implementation                      │
│  - Follow claude.md architecture guidelines     │
└─────────────┬───────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────┐
│           PHASE 1: CREATE ALL TESTS             │
│  Write comprehensive test suites for all code   │
│  - Create test files in /backend/tests/         │
│  - Cover happy path, errors, edge cases         │
│  - Use fixtures and mocks from conftest.py     │
└─────────────┬───────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────┐
│        PHASE 1: RUN TESTS & VERIFY              │
│  - All tests must pass (100%)                   │
│  - Coverage ≥80%                                │
│  - Quality gates pass (mypy, ruff, black)       │
│  - Check acceptance criteria in ROADMAP.md      │
└─────────────┬───────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────┐
│            COMMIT & MOVE TO PHASE 2             │
│  All phase 1 work committed with comprehensive  │
│  message detailing what was implemented         │
└─────────────┬───────────────────────────────────┘
              │
              ▼ (Repeat for Phase 2, 3, 4...)
```

---

## Step-by-Step Instructions

### Phase 1: Development (Code First)

#### 1. Read the Requirements

```bash
# Read the ROADMAP for Phase 1
cat ROADMAP.md | grep -A 200 "## Phase 1:"
```

Phase 1 tasks:
- 1.1 Backend Infrastructure ✓ (done)
- 1.2 Pydantic Models & Errors ✓ (done)
- 1.3 Planning Agent Service
- 1.4 Review Agent Service
- 1.5 Diagram Generator Integration
- 1.6 Image Converter Service
- 1.7 File Manager Service
- 1.8 Orchestrator Service
- 1.9 FastAPI Endpoints
- 1.10 Frontend Setup
- 1.11 Integration Testing

#### 2. Implement Each Task

For each task (starting with 1.3):

**Task 1.3: Planning Agent Service**

Create `/backend/app/services/planning_agent.py`:

```python
"""Planning Agent service for concept analysis."""

import asyncio
import json
from typing import Optional

from loguru import logger

from app.config import settings
from app.errors import PlanningError


class PlanningOutput:
    """Output structure for planning agent."""

    def __init__(
        self,
        concept: str,
        diagram_type: str,
        components: list,
        relationships: list,
        success_criteria: list,
        educational_level: str,
        key_insights: list,
    ):
        self.concept = concept
        self.diagram_type = diagram_type
        self.components = components
        self.relationships = relationships
        self.success_criteria = success_criteria
        self.educational_level = educational_level
        self.key_insights = key_insights


class PlanningAgent:
    """AI agent for analyzing concepts and creating diagram plans."""

    def __init__(self):
        """Initialize planning agent."""
        self.timeout = settings.planning_timeout
        self.gemini_api_key = settings.google_api_key
        # Import here to avoid circular imports
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.gemini_api_key)
            self.client = genai.GenerativeModel("gemini-2.5-flash")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {e}")
            raise PlanningError(f"Failed to initialize LLM: {e}")

    async def analyze(self, user_input: str, language: str = "en") -> PlanningOutput:
        """
        Analyze user input and create diagram plan.

        Args:
            user_input: User's question or topic
            language: Language code (en or zh)

        Returns:
            PlanningOutput with diagram specifications

        Raises:
            PlanningError: If analysis fails or times out
        """
        # Validate input
        if not user_input or not user_input.strip():
            raise PlanningError("Topic cannot be empty")
        if len(user_input) > 1000:
            raise PlanningError("Topic is too long (max 1000 characters)")

        try:
            # Run with timeout
            result = await asyncio.wait_for(
                self._analyze_internal(user_input, language),
                timeout=self.timeout,
            )
            logger.info(
                "Planning completed",
                concept=result.concept,
                diagram_type=result.diagram_type,
                components_count=len(result.components),
            )
            return result
        except asyncio.TimeoutError:
            raise PlanningError(
                f"Planning timed out after {self.timeout}s. Try a simpler topic."
            )
        except Exception as e:
            logger.error(f"Planning failed: {e}")
            raise PlanningError(f"Failed to analyze concept: {str(e)}")

    async def _analyze_internal(self, user_input: str, language: str) -> PlanningOutput:
        """Internal analysis implementation."""
        prompt = f"""You are an expert educational diagram designer. Analyze this concept and create a diagram plan.

User Input: {user_input}
Language: {language}

Respond in valid JSON with this structure:
{{
    "concept": "main concept",
    "diagram_type": "flowchart|mindmap|sequence|hierarchy",
    "components": ["element1", "element2", ...],
    "relationships": [{{"from": "a", "to": "b", "label": "relationship"}}, ...],
    "success_criteria": ["criterion1", "criterion2", ...],
    "educational_level": "8-10|11-13|14-15",
    "key_insights": ["insight1", "insight2", ...]
}}

Ensure:
- All components are relevant to the concept
- Diagram type matches the concept
- Relationships show clear connections
- Educational level matches student age group
- Success criteria are measurable"""

        try:
            response = self.client.generate_content(prompt)
            response_text = response.text

            # Parse JSON response
            # Handle case where response might have markdown code blocks
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]

            data = json.loads(response_text.strip())

            return PlanningOutput(
                concept=data["concept"],
                diagram_type=data["diagram_type"],
                components=data["components"],
                relationships=data["relationships"],
                success_criteria=data["success_criteria"],
                educational_level=data["educational_level"],
                key_insights=data["key_insights"],
            )
        except json.JSONDecodeError as e:
            raise PlanningError(f"Failed to parse planning response: {e}")
        except KeyError as e:
            raise PlanningError(f"Missing required field in planning response: {e}")
```

Follow this pattern for all remaining tasks.

#### 3. Test Basic Functionality

While implementing, do quick manual tests:

```bash
cd backend

# Test imports work
.venv/bin/python -c "from app.services.planning_agent import PlanningAgent; print('✓ Import successful')"

# Test configuration
.venv/bin/python -c "from app.config import settings; print(f'✓ Settings loaded: timeout={settings.planning_timeout}s')"
```

#### 4. Continue Implementation

Continue with tasks 1.4 through 1.11 following the same pattern.

---

### Phase 1: Testing (After All Code Complete)

#### Step 1: Create Test Files

Create test file `/backend/tests/services/test_planning_agent.py`:

```python
"""Tests for PlanningAgent service."""

import asyncio
import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.planning_agent import PlanningAgent
from app.errors import PlanningError


class TestPlanningAgent:
    """Planning agent tests."""

    def test_init_success(self):
        """Test successful agent initialization."""
        agent = PlanningAgent()
        assert agent is not None
        assert agent.timeout == 5

    def test_init_missing_api_key(self, monkeypatch):
        """Test error when API key missing."""
        monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
        with pytest.raises(PlanningError):
            PlanningAgent()

    @pytest.mark.asyncio
    async def test_analyze_valid_input(self):
        """Test successful planning analysis."""
        agent = PlanningAgent()

        # For real testing, mock the Gemini response
        with patch.object(agent.client, 'generate_content') as mock_generate:
            mock_response = MagicMock()
            mock_response.text = json.dumps({
                "concept": "Photosynthesis",
                "diagram_type": "flowchart",
                "components": ["Light", "Water", "CO2", "Glucose"],
                "relationships": [
                    {"from": "Light", "to": "Glucose", "label": "energy"}
                ],
                "success_criteria": ["All inputs shown", "Energy flow clear"],
                "educational_level": "11-13",
                "key_insights": ["Plants make food", "Sun is energy source"]
            })
            mock_generate.return_value = mock_response

            result = await agent.analyze("Explain photosynthesis")

            assert result.concept == "Photosynthesis"
            assert result.diagram_type == "flowchart"
            assert len(result.components) == 4

    @pytest.mark.asyncio
    async def test_analyze_empty_input(self):
        """Test error for empty input."""
        agent = PlanningAgent()
        with pytest.raises(PlanningError, match="cannot be empty"):
            await agent.analyze("")

    @pytest.mark.asyncio
    async def test_analyze_long_input(self):
        """Test error for input exceeding max length."""
        agent = PlanningAgent()
        with pytest.raises(PlanningError, match="too long"):
            await agent.analyze("x" * 1001)

    @pytest.mark.asyncio
    async def test_analyze_timeout(self):
        """Test timeout handling."""
        agent = PlanningAgent()
        agent.timeout = 0.001  # Set very short timeout

        with patch.object(agent.client, 'generate_content') as mock_generate:
            # Make it sleep to trigger timeout
            async def slow_response(*args, **kwargs):
                await asyncio.sleep(0.1)
                return MagicMock(text="{}")

            mock_generate.side_effect = slow_response

            with pytest.raises(PlanningError, match="timed out"):
                await agent.analyze("topic")

    @pytest.mark.asyncio
    async def test_analyze_invalid_json(self):
        """Test error handling for invalid JSON response."""
        agent = PlanningAgent()

        with patch.object(agent.client, 'generate_content') as mock_generate:
            mock_response = MagicMock()
            mock_response.text = "Not valid JSON"
            mock_generate.return_value = mock_response

            with pytest.raises(PlanningError, match="Failed to parse"):
                await agent.analyze("topic")

    @pytest.mark.asyncio
    async def test_analyze_missing_field(self):
        """Test error handling for missing required field."""
        agent = PlanningAgent()

        with patch.object(agent.client, 'generate_content') as mock_generate:
            mock_response = MagicMock()
            # Missing 'concept' field
            mock_response.text = json.dumps({
                "diagram_type": "flowchart",
                "components": ["A", "B"],
                "relationships": [],
                "success_criteria": [],
                "educational_level": "11-13",
                "key_insights": []
            })
            mock_generate.return_value = mock_response

            with pytest.raises(PlanningError, match="Missing required field"):
                await agent.analyze("topic")

    @pytest.mark.asyncio
    async def test_analyze_api_error(self):
        """Test error handling for API failures."""
        agent = PlanningAgent()

        with patch.object(agent.client, 'generate_content') as mock_generate:
            mock_generate.side_effect = Exception("API Error")

            with pytest.raises(PlanningError, match="Failed to analyze"):
                await agent.analyze("topic")
```

#### Step 2: Write Tests for All Modules

Create test files for:
- `tests/test_models.py` - Pydantic models
- `tests/test_config.py` - Configuration
- `tests/test_errors.py` - Error classes
- `tests/services/test_review_agent.py` - Review agent
- `tests/services/test_image_converter.py` - Image converter
- `tests/services/test_file_manager.py` - File manager
- `tests/services/test_orchestrator.py` - Orchestrator
- `tests/api/test_diagram.py` - API endpoints

---

### Phase 1: Testing (Run Tests)

#### Step 1: Run All Tests

```bash
cd backend

# Run all tests with coverage
.venv/bin/pytest tests/ --cov=app --cov-report=term-missing -v

# Example output:
# tests/services/test_planning_agent.py::TestPlanningAgent::test_init_success PASSED
# tests/services/test_planning_agent.py::TestPlanningAgent::test_analyze_valid_input PASSED
# ...
# ======================== 25 passed in 2.34s ========================
# Name                          Stmts   Miss  Cover
# ───────────────────────────────────────────────
# app/services/planning_agent    42      8    81%
# app/services/review_agent      50     15    70%
# ...
# TOTAL                         250     40    84%
```

#### Step 2: Check Coverage

Ensure 80%+ coverage:

```bash
# Show uncovered lines
.venv/bin/pytest tests/ --cov=app --cov-report=term-missing -v | grep -E "^app/" | grep -v "100%"

# If any module < 80%, add more tests
```

#### Step 3: Run Quality Gates

```bash
# Type checking
.venv/bin/mypy app/ --strict

# Linting
.venv/bin/ruff check app/ tests/

# Code formatting
.venv/bin/black --check app/ tests/

# If any fail, fix and re-run:
.venv/bin/black app/ tests/  # Auto-fix formatting
.venv/bin/ruff check app/ tests/ --fix  # Auto-fix linting
```

#### Step 4: Fix Issues

If tests fail or coverage is low:

1. Add missing tests for uncovered code
2. Fix code quality issues
3. Re-run tests until all pass

```bash
# Keep running tests while fixing
.venv/bin/pytest tests/ --cov=app -v
```

---

### Phase 1: Verification

#### Step 1: Check Acceptance Criteria

From ROADMAP.md Phase 1:

```bash
# Check each task's acceptance criteria

# Phase 1.3: Planning Agent
# [ ] Validates JSON parsing immediately
# [ ] Never returns partial/malformed JSON
# [ ] Raises error if parsing fails
# [ ] Timeout enforced (5s hard stop)
# [ ] Curriculum alignment guidance included

# Verify manually:
.venv/bin/python -c "
import asyncio
from app.services.planning_agent import PlanningAgent

async def test():
    agent = PlanningAgent()
    # This should work with real Gemini API
    # result = await agent.analyze('Explain water cycle')
    # print(f'✓ Planning works: {result.concept}')

# For now, just verify it initializes
print('✓ Planning agent initialized')
"
```

#### Step 2: Verify End-to-End (If Applicable)

For Phase 1.11, test full flow:

```bash
# Start services
.venv/bin/uvicorn app.main:app --reload &

# Test API
curl -X POST http://localhost:8000/api/diagram \
  -H "Content-Type: application/json" \
  -d '{"user_input":"Explain photosynthesis","language":"en"}'

# Check response has all required fields
# Should see: explanation, diagram_image, diagram_xml, export_urls, metadata
```

---

### Phase 1: Commit

Once all tests pass and quality gates are clean:

```bash
# Add all changes
git add app/ tests/

# Create comprehensive commit message
git commit -m "Phase 1: Implement backend services with full test coverage

Implementation:
- 1.3: Planning Agent Service with Gemini 2.5 Flash integration
  * Concept analysis and diagram type selection
  * Educational level assessment
  * Success criteria definition
  * JSON schema validation

- 1.4: Review Agent Service with quality control
  * XML parsing and validation
  * Scoring system (0-100 scale)
  * Iterative refinement (max 3 iterations)
  * Educational alignment checking

- 1.5: Diagram Generator integration
  * next-ai-draw-io API integration
  * XML generation and validation
  * Error handling with specific messages

- 1.6: Image Converter using Playwright
  * Playwright browser instance management
  * PNG rendering (1200px for display, 2400px for export)
  * SVG generation
  * Base64 encoding for inline display

- 1.7: File Manager with auto-cleanup
  * UUID-based file naming
  * Temporary file storage in /backend/temp
  * 1-hour auto-cleanup with background task
  * Path traversal prevention

- 1.8: Orchestrator Service
  * Pipeline coordination (Planning → Generation → Review → Image → Save)
  * Timeout management at each stage
  * Error handling and logging
  * Metadata tracking

- 1.9: FastAPI Endpoints
  * POST /api/diagram - Main generation endpoint
  * GET /api/export/{filename} - File downloads
  * Error response formatting
  * CORS configuration

Testing:
- 50+ test cases covering all services
- Happy path, error cases, edge cases
- Timeout and API failure scenarios
- 85% code coverage
- Mock fixtures for Gemini, Playwright, httpx

Quality:
- Type checking: 0 errors (mypy --strict)
- Linting: 0 violations (ruff)
- Formatting: All files formatted (black)
- Performance: All stages under timeout
- Documentation: Complete docstrings and comments"

# Push to remote
git push origin main
```

---

## Quick Reference

### Development Commands

```bash
cd backend

# Run tests
.venv/bin/pytest tests/ -v                    # Verbose
.venv/bin/pytest tests/ --cov=app            # With coverage
.venv/bin/pytest tests/services/ -v          # Specific module
.venv/bin/pytest -k "test_analyze" -v        # Specific test

# Quality gates
.venv/bin/mypy app/                          # Type check
.venv/bin/ruff check app/ tests/            # Lint
.venv/bin/black app/ tests/                  # Format

# Run app
.venv/bin/uvicorn app.main:app --reload     # Development
.venv/bin/uvicorn app.main:app --port 8001  # Different port
```

### Important Files

- `ROADMAP.md` - Phase-by-phase tasks (READ THIS FIRST)
- `claude.md` - Architecture and development guidelines
- `backend/README.md` - Backend setup instructions
- `backend/app/config.py` - Configuration/environment variables
- `backend/tests/conftest.py` - Test fixtures and mocks

### Environment Variables

Copy template and add API key:

```bash
cp backend/.env.example backend/.env

# Edit .env and set:
GOOGLE_API_KEY=your-api-key-here
DRAWIO_SERVICE_URL=http://localhost:3001
```

---

## Troubleshooting

### Tests failing with import errors

```bash
# Ensure dependencies are installed
cd backend
uv sync

# Ensure PYTHONPATH includes backend
export PYTHONPATH=/Users/GitHub/visuaLearn/backend:$PYTHONPATH
```

### Playwright installation issues

```bash
.venv/bin/playwright install chromium
.venv/bin/playwright install --with-deps chromium
```

### Gemini API errors

```bash
# Verify API key
echo $GOOGLE_API_KEY

# Test connection
.venv/bin/python -c "
import google.generativeai as genai
genai.configure(api_key='YOUR_KEY')
model = genai.GenerativeModel('gemini-2.5-flash')
response = model.generate_content('Hello')
print('✓ Gemini working')
"
```

### Coverage less than 80%

```bash
# See which lines are uncovered
.venv/bin/pytest tests/ --cov=app --cov-report=term-missing -v

# Add tests for uncovered lines
# Focus on high-risk code: error handling, complex logic
```

---

## Next Steps

1. ✓ Backend initialized with uv
2. ✓ Pydantic models and errors created
3. ✓ Test infrastructure set up
4. **→ Phase 1.3: Implement Planning Agent Service**
5. Phase 1.4-1.11: Continue implementation
6. Phase 1 Testing: Create and run test suite
7. Phase 1 Verification: Check acceptance criteria
8. Phase 1 Commit: Push all code
9. Phase 2: Repeat workflow

---

## Key Principles

- **Follow ROADMAP.md strictly** - It's your source of truth
- **Develop first, test second** - Complete all code for phase before writing tests
- **80%+ coverage required** - Phase not complete until tests pass
- **Zero fallback policy** - Raise errors, never use defaults
- **Quality gates must pass** - mypy, ruff, black all clean before commit
- **Commit comprehensively** - Detailed messages explaining what was implemented

Good luck! 🚀

