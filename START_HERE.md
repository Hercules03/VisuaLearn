# VisuaLearn - START HERE 🚀

**Welcome!** This file gets you started on VisuaLearn development.

---

## What You Have

✅ **Complete Backend** - Fully initialized with Python 3.11, FastAPI, Pydantic, pytest
✅ **Test Infrastructure** - Ready for 80%+ coverage tests
✅ **Documentation** - Comprehensive guides for each phase
✅ **Workflow** - Clear process: Develop → Test → Verify → Commit
✅ **Roadmap** - 4 phases over ~140 hours with detailed tasks

---

## Quick Setup (2 minutes)

### 1. Add Your Google API Key

```bash
cd backend
cp .env.example .env

# Edit .env and add:
# GOOGLE_API_KEY=your-actual-api-key
```

### 2. Verify Setup

```bash
.venv/bin/python -c "from app.main import app; print('✅ Backend ready')"
```

### 3. Start Coding

You're ready! Follow the steps below.

---

## Your Development Path

### Step 1: Read the Roadmap
```bash
# This is your task list
cat ROADMAP.md | head -100
```

**What you'll see:**
- Phase 1 (Weeks 1-2): 11 tasks to implement core MVP
- Phase 2 (Weeks 2-3): Error handling, polish, caching
- Phase 3 (Weeks 3-4): Testing, optimization, quality gates
- Phase 4 (Weeks 4-5): Docker, monitoring, deployment

### Step 2: Read Development Guide
```bash
# This is your workflow
cat DEVELOPMENT_GUIDE.md | head -150
```

**You'll learn:**
- How to implement each task (code first)
- How to write tests (after all code complete)
- How to run quality gates (mypy, ruff, black)
- How to verify progress against ROADMAP

### Step 3: Start Phase 1.3

**Current Status**: Phase 1.1-1.2 done ✅

**Next Task**: Phase 1.3 - Planning Agent Service

```bash
# Read what to build
grep -A 30 "### 1.3 Planning Agent Service" ROADMAP.md

# Implementation pattern:
# 1. Create app/services/planning_agent.py
# 2. Add Gemini integration with timeout handling
# 3. Implement concept analysis and diagram planning
# 4. Validate JSON output from API

# Keep it simple - focus on getting it working
```

### Step 4: Continue Phase 1

After 1.3, follow the same pattern for:
- 1.4 Review Agent Service
- 1.5 Diagram Generator
- 1.6 Image Converter
- 1.7 File Manager
- 1.8 Orchestrator
- 1.9 FastAPI Endpoints
- 1.10 Frontend Setup
- 1.11 Integration Testing

### Step 5: Test Phase 1

Once ALL code for Phase 1 is complete:

```bash
cd backend

# Create tests in tests/ directory
# Write comprehensive test cases

# Run tests
.venv/bin/pytest tests/ --cov=app --cov-report=term-missing -v

# Required: 80%+ coverage, all tests passing
# Required: Type checking, linting, formatting clean
```

### Step 6: Commit & Move to Phase 2

When Phase 1 tests all pass:

```bash
git add app/ tests/
git commit -m "Phase 1: Complete MVP implementation with tests

- All 11 phase 1 tasks implemented
- 85% test coverage
- All quality gates passing"

git push origin main
```

---

## Key Files

| File | Purpose |
|------|---------|
| **ROADMAP.md** | Your task list (READ THIS) |
| **DEVELOPMENT_GUIDE.md** | How to develop each task |
| **claude.md** | Architecture & guidelines |
| **PROJECT_STATUS.md** | Current progress |
| **backend/README.md** | Backend commands |
| **backend/.env.example** | Environment template |

---

## Essential Commands

```bash
cd backend

# Run tests
.venv/bin/pytest tests/ -v                    # See results
.venv/bin/pytest tests/ --cov=app            # Check coverage
.venv/bin/pytest tests/services/test_xxx.py -v  # Test one module

# Quality gates
.venv/bin/mypy app/                          # Type check
.venv/bin/ruff check app/ tests/            # Linting
.venv/bin/black app/ tests/                  # Code format

# Auto-fix
.venv/bin/black app/ tests/                  # Format all
.venv/bin/ruff check app/ tests/ --fix      # Fix linting issues

# Run app
.venv/bin/uvicorn app.main:app --reload     # Development server
```

---

## The Workflow (TL;DR)

For EACH Phase:

```
1. READ ROADMAP for phase tasks
   ↓
2. IMPLEMENT all code (follow claude.md architecture)
   ├─ Don't write tests yet
   ├─ Focus on getting it working
   └─ Use print() for quick debugging
   ↓
3. WRITE comprehensive test suite
   ├─ Create test files in tests/
   ├─ Cover happy path, errors, edge cases
   └─ Use fixtures from conftest.py
   ↓
4. RUN tests & quality gates
   ├─ pytest tests/ --cov=app    (target 80%+ coverage)
   ├─ mypy app/                   (type checking)
   ├─ ruff check app/             (linting)
   └─ black --check app/          (formatting)
   ↓
5. FIX issues until all pass
   ├─ Add tests for uncovered code
   ├─ Fix code quality issues
   └─ Run tests until green
   ↓
6. VERIFY against ROADMAP acceptance criteria
   ├─ Check all requirements met
   ├─ Test manually if applicable
   └─ Ready for production
   ↓
7. COMMIT with comprehensive message
   └─ Push to main when ready
   ↓
→ Start next phase
```

---

## Example: Phase 1.3 (Planning Agent)

**Task**: Implement planning agent to analyze concepts

**Implementation**:
```python
# backend/app/services/planning_agent.py
class PlanningAgent:
    def __init__(self):
        # Initialize Gemini client
        pass
    
    async def analyze(self, user_input: str) -> PlanningOutput:
        # Analyze concept using Gemini 2.5 Flash
        # Return diagram specs (components, relationships, etc)
        # Raise PlanningError on timeout/failure
        pass
```

**Testing** (after code complete):
```python
# backend/tests/services/test_planning_agent.py
class TestPlanningAgent:
    async def test_analyze_valid_input(self):
        # Should parse Gemini response correctly
        pass
    
    async def test_analyze_empty_input(self):
        # Should raise PlanningError
        pass
    
    async def test_analyze_timeout(self):
        # Should handle 5s timeout
        pass
    # ... more tests covering errors and edge cases
```

**Quality Gates**:
```bash
.venv/bin/pytest tests/services/test_planning_agent.py --cov=app.services.planning_agent
# Expected: All tests pass, 90%+ coverage

.venv/bin/mypy app/services/planning_agent.py
# Expected: No errors

.venv/bin/ruff check app/services/planning_agent.py
# Expected: No issues
```

---

## Important Notes

### ⚠️ Do This
✅ Read ROADMAP.md before starting each task
✅ Implement all code first (for phase)
✅ Write tests AFTER code is complete
✅ Ensure 80%+ test coverage before moving on
✅ Run quality gates: mypy, ruff, black
✅ Commit with comprehensive messages

### ❌ Don't Do This
❌ Write tests before code
❌ Skip quality gate checks
❌ Use fallback/default values (raise errors instead)
❌ Commit without tests passing
❌ Leave TODOs in code
❌ Hardcode configuration

---

## Getting Help

| Question | Answer |
|----------|--------|
| "What should I build?" | Read ROADMAP.md section for current phase |
| "How do I build it?" | Follow DEVELOPMENT_GUIDE.md |
| "What's the architecture?" | See claude.md Architecture Principles |
| "How do I run tests?" | See Quick Commands above |
| "What commands are available?" | See backend/README.md Development section |

---

## Status Summary

```
✅ Backend infrastructure initialized
✅ Dependencies installed (68 packages)
✅ Configuration system ready
✅ Test framework configured
✅ Quality tools installed
✅ Documentation complete

🎯 READY TO START PHASE 1.3
```

---

## Next 5 Minutes

```bash
# 1. Set up environment
cd backend
cp .env.example .env
# (edit .env, add GOOGLE_API_KEY)

# 2. Verify it works
.venv/bin/python -c "from app.main import app; print('✅ Ready')"

# 3. Read the roadmap
cat ../ROADMAP.md | grep "### 1.3" -A 50

# 4. Create the file
touch app/services/planning_agent.py

# 5. Start implementing!
# (Follow DEVELOPMENT_GUIDE.md)
```

---

## You're All Set! 🎉

The foundation is complete. You have everything you need to build VisuaLearn.

**Your mission**: Follow the ROADMAP, implement Phase 1, write tests, verify quality.

**Timeline**: ~40-50 hours for Phase 1 (2 weeks)

**Success**: All tests passing, 80%+ coverage, quality gates clean

---

**Questions?** Check the relevant document:
- ROADMAP.md → Task details
- DEVELOPMENT_GUIDE.md → How to build
- claude.md → Architecture guidelines

**Ready?** Start with Phase 1.3! 🚀

