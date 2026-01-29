# VisuaLearn Project Roadmap

## Project Timeline Overview

```
Phase 1: MVP Core           [Week 1-2]  Backend services + Basic UI
Phase 2: Integration        [Week 2-3]  Full pipeline + Polish
Phase 3: Testing & Opt      [Week 3-4]  Quality gates + Performance
Phase 4: Deployment         [Week 4-5]  Launch readiness
```

---

## Phase 1: MVP Core Development (Weeks 1-2)

### Goal
Implement core diagram generation pipeline with working UI. Users can ask a question and receive a diagram with explanation.

### 1.1 Backend Infrastructure Setup

**Tasks**:
- [ ] Create project directory structure (backend/, frontend/, docker-compose.yml)
- [ ] Set up Python environment (Python 3.11+, venv)
- [ ] Create requirements.txt with dependencies:
  - `fastapi`, `uvicorn`, `pydantic`, `pydantic-settings`
  - `google-generativeai` (Gemini SDK)
  - `playwright`, `httpx`, `loguru`
  - `python-dotenv`, `pytest`, `pytest-cov`
- [ ] Create .env.example with required variables
- [ ] Set up app/ directory structure:
  ```
  backend/
  ├── app/
  │   ├── main.py           # FastAPI entry point
  │   ├── config.py         # Settings/environment
  │   ├── api/
  │   │   └── diagram.py    # POST /api/diagram endpoint
  │   ├── models/
  │   │   └── schemas.py    # Pydantic models
  │   ├── services/
  │   │   ├── orchestrator.py
  │   │   ├── planning_agent.py
  │   │   ├── review_agent.py
  │   │   ├── image_converter.py
  │   │   └── file_manager.py
  │   └── errors.py         # Custom exceptions
  ├── temp/                 # Auto-cleanup temp files
  ├── tests/
  └── requirements.txt
  ```

**Acceptance Criteria**:
- FastAPI app starts without errors
- Environment variables load from .env
- Temp directory exists with proper permissions
- All imports work correctly

**Estimated Work**: 2-3 hours

---

### 1.2 Pydantic Models & Error Handling

**Tasks**:
- [ ] Create DiagramRequest model (user_input, language)
- [ ] Create DiagramResponse model (explanation, diagram_image, export_urls, metadata)
- [ ] Create custom exception hierarchy:
  - `VisuaLearnError` (base)
  - `InputValidationError`
  - `PlanningError`
  - `GenerationError`
  - `ReviewError`
  - `RenderingError`
- [ ] Implement error response format (error, message, details)
- [ ] Add input validation (1-1000 chars, language en|zh)

**Code Location**: `backend/app/models/schemas.py`, `backend/app/errors.py`

**Acceptance Criteria**:
- Valid requests pass validation
- Invalid requests raise ValidationError
- Custom exceptions inherit properly
- Error responses are structured

**Estimated Work**: 1-2 hours

---

### 1.3 Planning Agent Service

**Tasks**:
- [ ] Create `planning_agent.py` service
- [ ] Implement `analyze(user_input: str, language: str)` method
- [ ] Set up Gemini API client with GOOGLE_API_KEY
- [ ] Create structured prompt for planning:
  - Ask for: concept, diagram_type, components, relationships, success_criteria, educational_level
  - Require JSON output format
  - Include curriculum alignment guidance
- [ ] Implement JSON parsing with validation
- [ ] Add timeout handling (5s hard stop)
- [ ] Add error handling for API failures
- [ ] Log planning outputs for debugging

**Code Example Needed**:
```python
async def analyze(self, user_input: str, language: str = "en") -> PlanningOutput:
    """Analyze concept and create diagram plan"""
    # Timeout handling
    # Gemini API call
    # JSON parsing
    # Validation
    # Return PlanningOutput
    pass
```

**Acceptance Criteria**:
- Returns valid PlanningOutput JSON
- Completes within 5s timeout
- Handles API errors gracefully
- Validates JSON structure

**Estimated Work**: 3-4 hours

---

### 1.4 Review Agent Service

**Tasks**:
- [ ] Create `review_agent.py` service
- [ ] Implement `validate(xml: str, plan: PlanningOutput, iteration: int)` method
- [ ] Create structured prompt for review:
  - Parse XML and check against plan
  - Score 0-100 based on criteria
  - Identify missing elements
  - Generate refinement instructions
- [ ] Implement approval logic:
  - Score ≥90: Auto-approve
  - Score 70-89: Request refinement
  - Score <70 on iteration 3: Accept anyway
- [ ] Add timeout handling (3s per iteration)
- [ ] Track iteration count (max 3)
- [ ] Return review feedback with actionable instructions

**Acceptance Criteria**:
- Returns valid ReviewOutput
- Scores consistently
- Generates specific refinement instructions
- Respects iteration limits

**Estimated Work**: 3-4 hours

---

### 1.5 Diagram Generator Service

**Tasks**:
- [ ] Create `image_converter.py` service (for now, stub with placeholder)
- [ ] Set up integration with next-ai-draw-io service:
  - HTTP client (httpx) to call next-ai-draw-io API
  - URL from config (DRAWIO_SERVICE_URL)
  - POST request with planning JSON
- [ ] Implement XML validation using lxml
- [ ] Add timeout handling (12s hard stop)
- [ ] Handle generation errors (invalid XML, timeout, API failure)
- [ ] For now: Return mock XML for testing

**Code Example**:
```python
async def generate(self, plan: PlanningOutput) -> str:
    """Generate draw.io XML from plan"""
    # Call next-ai-draw-io API
    # Validate XML with lxml
    # Handle errors
    # Return XML string
    pass
```

**Acceptance Criteria**:
- Successfully calls next-ai-draw-io API
- Validates XML structure
- Handles errors with specific messages
- Works with timeout

**Estimated Work**: 2-3 hours

---

### 1.6 Image Converter Service

**Tasks**:
- [ ] Create `image_converter.py` service (real implementation)
- [ ] Set up Playwright browser instance:
  - Initialize on app startup
  - Reuse across requests
  - Handle cleanup properly
- [ ] Implement `render_to_png(xml: str)` method:
  - Use Playwright to load draw.io XML
  - Render to PNG at 1200px width
  - Return PNG bytes
- [ ] Implement Base64 encoding for inline display
- [ ] Add parallel PNG + SVG rendering
- [ ] Implement image caching (in-memory, session-based)
- [ ] Add timeout (4s hard stop)

**Acceptance Criteria**:
- Renders PNG from valid XML
- Text readable on mobile (min 12px)
- Encodes to Base64 correctly
- Completes within 4s

**Estimated Work**: 4-5 hours

---

### 1.7 File Manager Service

**Tasks**:
- [ ] Create `file_manager.py` service
- [ ] Implement file operations:
  - Generate UUID filenames
  - Save PNG, SVG, XML to `/backend/temp`
  - Create download URLs
  - Track file creation time
- [ ] Implement cleanup task:
  - Run every 10 minutes
  - Delete files >1 hour old
  - Log deletions
- [ ] Add security validation:
  - Path traversal prevention
  - Extension validation (png, svg, xml only)
  - Size limits (5MB max)
- [ ] Handle atomic writes (use tempfile library)

**Code Example**:
```python
async def save_files(self, png_bytes: bytes, svg_bytes: bytes, xml_str: str) -> ExportUrls:
    """Save diagram files and return download URLs"""
    # Generate UUID
    # Atomic write to temp directory
    # Create URLs
    # Schedule cleanup
    # Return ExportUrls
    pass
```

**Acceptance Criteria**:
- Files saved with UUID names
- Cleanup task runs and deletes old files
- Path traversal blocked
- Size limits enforced

**Estimated Work**: 2-3 hours

---

### 1.8 Orchestrator Service

**Tasks**:
- [ ] Create `orchestrator.py` service
- [ ] Implement `generate_diagram(request: DiagramRequest)` method
- [ ] Coordinate pipeline:
  1. Validate input
  2. Call planning agent (3s timeout)
  3. Call diagram generator (12s timeout)
  4. Call review agent (3s timeout, max 3 iterations)
  5. Call image converter (4s timeout)
  6. Save files
  7. Return response
- [ ] Add error handling at each stage with specific exceptions
- [ ] Track timing for each stage
- [ ] Log full execution flow
- [ ] Stream explanation text to frontend

**Code Flow**:
```
Input → Planning → Generation → Review [loop if needed] → Image → Save → Response
```

**Acceptance Criteria**:
- Full pipeline executes without errors
- Timeouts enforced at each stage
- Errors caught and reported
- Timing tracked and logged

**Estimated Work**: 3-4 hours

---

### 1.9 FastAPI Endpoint

**Tasks**:
- [ ] Create `api/diagram.py` with POST /api/diagram endpoint
- [ ] Implement request handling:
  - Validate DiagramRequest
  - Call orchestrator
  - Return DiagramResponse
  - Handle errors with proper HTTP status codes
- [ ] Add stream support for explanation text (optional, can add later)
- [ ] Create GET /api/export/{filename} endpoint
- [ ] Implement file download:
  - Validate filename
  - Check file exists
  - Return with proper Content-Type and Content-Disposition
  - Handle 404 for missing files
- [ ] Add CORS headers (allow frontend localhost)
- [ ] Add request logging middleware

**Acceptance Criteria**:
- POST /api/diagram returns valid DiagramResponse
- GET /api/export/{filename} downloads file
- Errors return proper HTTP status (400/500)
- File validation prevents path traversal

**Estimated Work**: 2-3 hours

---

### 1.10 Frontend Setup & Chat UI

**Tasks**:
- [ ] Initialize React project (Vite + TypeScript)
- [ ] Set up directory structure:
  ```
  frontend/
  ├── src/
  │   ├── components/
  │   │   ├── ChatInterface.tsx
  │   │   ├── DiagramDisplay.tsx
  │   │   └── ExportButtons.tsx
  │   ├── hooks/
  │   │   └── useDiagram.ts
  │   ├── types/
  │   │   └── diagram.ts
  │   ├── App.tsx
  │   └── main.tsx
  ├── package.json
  └── tailwind.config.js
  ```
- [ ] Configure Tailwind CSS + shadcn/ui
- [ ] Create ChatInterface component:
  - Input field for user question
  - Send button
  - Loading state
  - Chat history display
- [ ] Create DiagramDisplay component:
  - Show explanation text
  - Display diagram image
  - Show loading states
- [ ] Create ExportButtons component:
  - PNG download button
  - SVG download button
  - XML download button
- [ ] Implement API client (axios):
  - POST /api/diagram
  - GET /api/export/{filename}
  - Error handling with toast messages

**Acceptance Criteria**:
- Chat input works
- Can submit question
- Loading states display
- API calls successful
- Downloads work

**Estimated Work**: 5-6 hours

---

### 1.11 Integration Testing (Manual)

**Tasks**:
- [ ] Start next-ai-draw-io service (Docker or local)
- [ ] Start FastAPI backend
- [ ] Start React frontend
- [ ] Test full flow:
  1. Enter "Explain photosynthesis"
  2. Verify planning agent output
  3. Verify diagram generation
  4. Verify review agent approval
  5. Verify image rendering
  6. Verify diagram display
  7. Test PNG/SVG/XML downloads
- [ ] Test error cases:
  - Empty input
  - Very long input
  - Invalid topic
  - Timeout handling
- [ ] Check performance:
  - Planning time
  - Generation time
  - Review time
  - Image conversion time
  - Total end-to-end time (target <15s)

**Acceptance Criteria**:
- Full flow works end-to-end
- Diagram displays correctly
- Exports work
- Errors handled gracefully
- Performance acceptable

**Estimated Work**: 2-3 hours

---

## Phase 2: Integration & Polish (Weeks 2-3)

### Goal
Complete pipeline with proper error handling, content filtering, and UI polish. Ensure quality meets standards.

### 2.1 Content Filtering & Validation

**Tasks**:
- [ ] Implement content filter in planning agent:
  - Check for violent/graphic content
  - Check for adult/explicit material
  - Check for spam/nonsensical requests
  - Check for harmful instructions
  - Check for PII requests
- [ ] Add age-appropriate validation:
  - Analyze concept complexity
  - Ensure language level appropriate
  - Flag inappropriate topics
- [ ] Reject invalid requests early with clear error messages
- [ ] Log filtered requests for monitoring

**Acceptance Criteria**:
- Blocks inappropriate content
- Provides clear rejection reasons
- Allows valid educational content
- Logs all filters

**Estimated Work**: 2-3 hours

---

### 2.2 AI-Generated Content Disclaimer

**Tasks**:
- [ ] Add disclaimer to every response:
  - "⚠️ This diagram is AI-generated. Please verify with your teacher or textbook for accuracy."
- [ ] Include in explanation text
- [ ] Display in UI with warning icon
- [ ] Store in metadata for tracking

**Acceptance Criteria**:
- Disclaimer appears on all diagrams
- Formatted clearly in UI
- Easy to understand

**Estimated Work**: 1 hour

---

### 2.3 Enhanced Error Handling

**Tasks**:
- [ ] Review all error paths in orchestrator
- [ ] Ensure all external API calls have timeouts
- [ ] Implement graceful degradation:
  - If review agent fails: return diagram with warning
  - If image conversion fails: return XML + explanation
  - Never return null or incomplete responses
- [ ] Create user-friendly error messages:
  - "Planning failed. Try a simpler topic."
  - "Generation timed out. This topic might be too complex."
  - "Image rendering failed. Try downloading XML instead."
- [ ] Log all errors for debugging
- [ ] Return structured error responses

**Code Pattern**:
```python
try:
    result = await some_operation()
except TimeoutError:
    logger.error("Operation timed out")
    raise OperationError("This is taking longer than expected. Try a simpler topic.")
```

**Acceptance Criteria**:
- All errors caught and logged
- User-friendly messages
- No silent failures
- Appropriate HTTP status codes

**Estimated Work**: 2-3 hours

---

### 2.4 Logging Infrastructure

**Tasks**:
- [ ] Configure Loguru:
  - Console output (DEBUG in development, INFO in production)
  - File output (rotated logs)
  - Structured logging with context
- [ ] Add logging at key points:
  - Planning start/end with timing
  - Generation start/end with XML size
  - Review iterations with scores
  - Image conversion with file size
  - File save/cleanup with path
- [ ] Track key metrics:
  - planning_time, generation_time, review_time, image_time, total_time
  - review_score, review_iterations, approved
  - user_input (sanitized), diagram_type, language
- [ ] Create log parsing helpers for debugging

**Acceptance Criteria**:
- Structured logs easy to parse
- All key operations logged
- Metrics tracked for analysis
- Log rotation working

**Estimated Work**: 2-3 hours

---

### 2.5 Configuration Management

**Tasks**:
- [ ] Complete BaseSettings class in config.py
- [ ] Add all timeout settings:
  - PLANNING_TIMEOUT=5
  - GENERATION_TIMEOUT=12
  - REVIEW_TIMEOUT=3
  - IMAGE_TIMEOUT=4
  - REVIEW_MAX_ITERATIONS=3
- [ ] Add file management settings:
  - TEMP_DIR=./backend/temp
  - TEMP_FILE_TTL=3600
  - CLEANUP_INTERVAL=600
  - MAX_FILE_SIZE=5242880 (5MB)
- [ ] Add performance tuning settings:
  - CACHE_SIZE_MB=500
  - CACHE_TTL_SECONDS=3600
- [ ] Validate all required settings on startup
- [ ] Prevent hardcoded values (use config everywhere)

**Acceptance Criteria**:
- All config from environment variables
- No hardcoded values
- Validation on startup
- Sensible defaults

**Estimated Work**: 1-2 hours

---

### 2.6 Caching Implementation

**Tasks**:
- [ ] Implement in-memory query cache:
  - Store Gemini responses for identical inputs
  - 1-hour TTL
  - Max 500MB size
  - Clear on eviction
- [ ] Implement image cache:
  - Cache identical rendered PNG/SVG
  - Session-based (clear on browser close)
- [ ] Add cache statistics:
  - Hit rate
  - Miss count
  - Cache size
  - Eviction count
- [ ] Use cache in orchestrator:
  - Check planning cache before API call
  - Check image cache before render

**Acceptance Criteria**:
- Cache hits reduce API calls
- TTL enforced correctly
- Size limits respected
- Cache statistics tracked

**Estimated Work**: 3-4 hours

---

### 2.7 Frontend Polish

**Tasks**:
- [ ] Improve ChatInterface:
  - Better input styling
  - Send button states (enabled/disabled)
  - Enter key to send
  - Clear button to reset chat
  - Conversation history display
- [ ] Improve DiagramDisplay:
  - Skeleton loading state
  - Progressive loading (explanation first, then diagram)
  - Error state with retry button
  - Metadata display (iterations, score, time)
- [ ] Improve ExportButtons:
  - Loading state during download
  - Success toast after download
  - Error handling
  - Visual feedback
- [ ] Add mobile responsiveness:
  - Touch-friendly buttons (44x44px min)
  - Readable on small screens
  - Stack layout vertically on mobile
- [ ] Accessibility improvements:
  - ARIA labels on buttons
  - Keyboard navigation (Tab, Enter)
  - Screen reader support
  - High contrast mode

**Acceptance Criteria**:
- Responsive on mobile/tablet/desktop
- Loading states clear
- Error handling graceful
- Accessible to keyboard and screen reader users

**Estimated Work**: 4-5 hours

---

### 2.8 Environment Setup Automation

**Tasks**:
- [ ] Create setup script (setup.sh):
  - Install Python dependencies
  - Install Playwright
  - Create temp directory
  - Generate .env from .env.example
- [ ] Create start script (start.sh):
  - Check environment variables
  - Start next-ai-draw-io (Docker)
  - Start FastAPI backend
  - Start React frontend
  - Open browser to http://localhost:3000
- [ ] Create docker-compose.yml:
  - FastAPI service
  - next-ai-draw-io service
  - Volume mounts for temp files
- [ ] Documentation (README.md):
  - Quick start instructions
  - Environment setup
  - Common issues and solutions
  - Architecture diagram

**Acceptance Criteria**:
- Setup script works on macOS/Linux
- All services start correctly
- Docker compose works
- README is clear and complete

**Estimated Work**: 2-3 hours

---

## Phase 3: Testing & Optimization (Weeks 3-4)

### Goal
Achieve 80%+ test coverage, <15s performance, and quality gate validation.

### 3.1 Unit Tests

**Tasks**:
- [ ] Test Pydantic models (schemas.py):
  - Valid inputs pass
  - Invalid inputs raise ValidationError
  - Boundary conditions
- [ ] Test planning agent:
  - JSON parsing
  - Error handling
  - Timeout handling
  - Output validation
- [ ] Test review agent:
  - Scoring logic
  - Approval threshold
  - Iteration limits
  - Refinement instructions
- [ ] Test file manager:
  - UUID generation
  - File saving
  - File cleanup
  - Path traversal prevention
- [ ] Test error handling:
  - All exception types raised correctly
  - Error messages user-friendly
- [ ] Create test fixtures for mocking:
  - Mock Gemini API responses
  - Mock next-ai-draw-io responses
  - Mock Playwright rendering

**Target Coverage**: 80%+ lines

**Acceptance Criteria**:
- All tests pass
- Coverage report generated
- Mocking patterns consistent
- Test naming clear

**Estimated Work**: 6-8 hours

---

### 3.2 Integration Tests

**Tasks**:
- [ ] Test full diagram generation flow:
  - Planning → Generation → Review → Image → Save
  - Verify all stages complete
  - Check metadata accuracy
- [ ] Test error scenarios:
  - Invalid input handling
  - API timeout handling
  - XML validation failures
  - File save failures
- [ ] Test review iteration loop:
  - Iteration 1 with low score → refines
  - Iteration 2 with low score → refines
  - Iteration 3 with any score → accepts
- [ ] Test file operations:
  - Files saved correctly
  - URLs generated correctly
  - Files cleanup after TTL
- [ ] Performance tests:
  - Each stage under timeout
  - Total <15s
  - Caching reduces API calls

**Acceptance Criteria**:
- All integration tests pass
- Error scenarios handled
- Performance targets met
- Database (if added) tested

**Estimated Work**: 5-7 hours

---

### 3.3 E2E Tests (Playwright)

**Tasks**:
- [ ] Test user workflows:
  - Load homepage
  - Enter question
  - Submit and wait for diagram
  - Verify diagram displays
  - Download PNG/SVG/XML
  - Test error message display
- [ ] Test mobile responsiveness:
  - Viewport 375x667 (iPhone)
  - Viewport 768x1024 (iPad)
  - Touch interactions work
- [ ] Test accessibility:
  - Keyboard navigation (Tab through elements)
  - Screen reader (ARIA labels)
  - Focus management
- [ ] Cross-browser testing:
  - Chrome/Chromium
  - Firefox
  - Safari (if possible)

**Acceptance Criteria**:
- All user workflows pass
- Mobile layouts correct
- Accessibility passing
- Cross-browser compatible

**Estimated Work**: 5-6 hours

---

### 3.4 Performance Optimization

**Tasks**:
- [ ] Profile each stage with timing:
  - Identify bottlenecks
  - Measure baseline performance
- [ ] Optimize planning agent:
  - Reduce prompt verbosity (still accurate)
  - Cache similar requests
  - Use faster prompt patterns
- [ ] Optimize image conversion:
  - Parallel PNG + SVG rendering
  - Browser instance pooling
  - Image caching
  - Compression optimization
- [ ] Optimize file operations:
  - Async I/O for all file writes
  - Batch cleanup operations
  - Efficient UUID generation
- [ ] Add performance monitoring:
  - Track p95 latency
  - Alert if >15s
  - Dashboard metrics (nice-to-have)

**Targets**:
- Planning: 3s (5s max)
- Generation: 8s (12s max)
- Review: 2s per iteration (3s max)
- Image: 2s (4s max)
- Total: 15s (20s max)

**Acceptance Criteria**:
- P95 latency <15s
- All stages under timeout
- Performance metrics tracked

**Estimated Work**: 4-5 hours

---

### 3.5 Quality Gates Implementation

**Tasks**:
- [ ] Implement pre-commit checks:
  - pytest (all tests pass)
  - mypy (type checking)
  - ruff (linting)
  - black (formatting)
- [ ] Create quality gates checklist:
  - [ ] Tests pass (80%+ coverage)
  - [ ] Type checking passes
  - [ ] Linting passes
  - [ ] Formatting correct
  - [ ] No hardcoded config
  - [ ] Timeouts on all external calls
  - [ ] Error handling explicit (no fallbacks)
  - [ ] Documentation updated
  - [ ] Performance <15s p95
- [ ] Create pre-commit hook (optional):
  - Run tests
  - Run linting/type check
  - Block commit if failures
- [ ] Document quality standards

**Acceptance Criteria**:
- All quality gates defined
- Can be checked automatically
- Pre-commit hook working
- Standards documented

**Estimated Work**: 2-3 hours

---

### 3.6 Documentation

**Tasks**:
- [ ] Create API documentation:
  - POST /api/diagram (request/response examples)
  - GET /api/export/{filename}
  - Error response formats
  - Example cURL commands
- [ ] Create developer guide:
  - Architecture overview
  - How to add new features
  - Common debugging patterns
  - Testing workflow
- [ ] Update claude.md with implementation notes
- [ ] Create architecture diagrams:
  - System architecture
  - Request flow diagram
  - Agent pipeline diagram
- [ ] Deployment guide (draft for Phase 4)

**Acceptance Criteria**:
- API fully documented
- Developer guide complete
- Examples runnable
- Diagrams clear

**Estimated Work**: 3-4 hours

---

## Phase 4: Deployment Readiness (Week 4-5)

### Goal
Production-ready deployment with monitoring, health checks, and deployment procedures.

### 4.1 Docker Setup

**Tasks**:
- [ ] Create Dockerfile for FastAPI:
  - Python 3.11 base image
  - Install dependencies
  - Copy app code
  - Expose port 8000
  - Health check endpoint
- [ ] Create Dockerfile for frontend:
  - Node 18 base image
  - Build React app
  - Serve with nginx
  - Expose port 3000
- [ ] Complete docker-compose.yml:
  - FastAPI service
  - next-ai-draw-io service
  - Frontend service (optional)
  - Volume mounts for temp files
  - Environment variables
  - Port mappings
- [ ] Create .dockerignore files (exclude node_modules, venv, etc.)

**Acceptance Criteria**:
- Docker builds successfully
- docker-compose up starts all services
- Services communicate correctly
- Volumes persist correctly

**Estimated Work**: 2-3 hours

---

### 4.2 Health Checks & Monitoring

**Tasks**:
- [ ] Implement `/health` endpoint:
  - Check Gemini API connectivity
  - Check next-ai-draw-io connectivity
  - Check Playwright browser status
  - Check disk space
  - Check memory usage
  - Return JSON with status
- [ ] Add prometheus metrics (nice-to-have):
  - Request count
  - Request duration
  - Error rate
  - Cache hit rate
- [ ] Create monitoring dashboard (nice-to-have):
  - Response times
  - Error rates
  - API usage
  - Resource utilization
- [ ] Set up alerting:
  - Uptime monitoring
  - Performance degradation alerts
  - Error rate spikes

**Acceptance Criteria**:
- Health check endpoint working
- Metrics collected
- Alerts configured (if applicable)

**Estimated Work**: 3-4 hours

---

### 4.3 Deployment Configuration

**Tasks**:
- [ ] Create deployment guides:
  - Manual deployment (EC2, VPS)
  - Railway deployment (recommended for MVP)
  - Render deployment (alternative)
  - Vercel frontend deployment
- [ ] Environment setup for production:
  - Production .env template
  - Database setup (if added)
  - S3/R2 configuration (for exports)
  - CDN configuration (optional)
- [ ] Create pre-deployment checklist:
  - All tests pass
  - No hardcoded configuration
  - Secrets in environment variables
  - API keys rotated
  - Performance benchmarked
  - Error handling complete
  - Logging configured
  - Health checks working
  - Monitoring active
- [ ] Create runbook for incidents:
  - Common errors and solutions
  - Rollback procedures
  - Data recovery steps
  - Support escalation

**Acceptance Criteria**:
- Deployment guide clear and testable
- Pre-deployment checklist complete
- Runbook covers common issues

**Estimated Work**: 3-4 hours

---

### 4.4 Security Hardening

**Tasks**:
- [ ] API security:
  - CORS configuration (frontend domain)
  - Rate limiting (optional, depends on scale)
  - Input validation strict
  - SQL injection prevention (if database added)
  - XSS prevention in frontend
- [ ] Secrets management:
  - No secrets in git
  - Environment variables only
  - Secrets rotation procedure
  - Key scanning tool (optional)
- [ ] HTTPS/TLS:
  - Enable HTTPS in production
  - Certificate management
  - SSL/TLS configuration
- [ ] Content security:
  - Age-appropriate filtering
  - PII protection
  - Content moderation logging
- [ ] Dependency security:
  - Vulnerability scanning
  - Dependency updates
  - Lock files for reproducibility

**Acceptance Criteria**:
- CORS properly configured
- No secrets in repository
- HTTPS enabled
- Vulnerability scan clean

**Estimated Work**: 2-3 hours

---

### 4.5 Performance Tuning for Scale

**Tasks**:
- [ ] Load testing:
  - Test with 100 concurrent users
  - Measure response times
  - Identify bottlenecks
  - Adjust scaling parameters
- [ ] Database connection pooling (if DB added):
  - Configure pool size
  - Test under load
- [ ] API rate limiting:
  - Set limits per IP/user
  - Handle gracefully
  - Configure backoff
- [ ] Caching strategy refinement:
  - Cache hot endpoints
  - Optimize TTL values
  - Monitor cache effectiveness
- [ ] Resource optimization:
  - Memory profiling
  - CPU optimization
  - Disk I/O optimization

**Acceptance Criteria**:
- Load test results documented
- Scales to target (1000 concurrent for MVP)
- Bottlenecks identified and addressed
- Caching effective

**Estimated Work**: 4-5 hours

---

### 4.6 Final Testing & Validation

**Tasks**:
- [ ] Full regression test:
  - All features working
  - All edge cases handled
  - Performance targets met
- [ ] UAT checklist:
  - Teachers can generate diagrams (5+ types)
  - Students find it easy to use
  - Diagrams are educationally sound
  - Export works (PNG, SVG, XML)
  - Error messages clear
- [ ] Security validation:
  - No vulnerabilities
  - Secrets safe
  - Content filtering working
  - Age-appropriate validation passing
- [ ] Performance validation:
  - <15s end-to-end (95th percentile)
  - <0.5% error rate
  - 99.5% uptime (simulated)

**Acceptance Criteria**:
- All tests pass (green build)
- UAT sign-off
- Security validation complete
- Performance targets met

**Estimated Work**: 2-3 hours

---

### 4.7 Launch Preparation

**Tasks**:
- [ ] Marketing materials:
  - Homepage copy
  - Feature highlights
  - Educational value proposition
  - Call-to-action
- [ ] Social media setup:
  - Twitter/X account
  - Educational community posts
  - Screenshot/demo content
- [ ] Beta signup (optional):
  - Beta tester recruitment
  - Feedback collection form
  - Early access list
- [ ] Analytics setup:
  - Google Analytics
  - Error tracking (Sentry)
  - Performance monitoring
- [ ] Support setup:
  - Contact form
  - Email support template
  - FAQ document

**Acceptance Criteria**:
- Marketing materials ready
- Analytics integrated
- Support email working
- Ready for public announcement

**Estimated Work**: 3-4 hours

---

## Summary of Work Breakdown

| Phase | Week | Main Deliverables | Estimated Hours |
|-------|------|-------------------|-----------------|
| Phase 1: MVP Core | 1-2 | Backend services, Frontend UI, Basic integration | 40-50 hours |
| Phase 2: Integration | 2-3 | Error handling, Logging, Caching, Polish | 25-30 hours |
| Phase 3: Testing & Optimization | 3-4 | Tests (80%+ coverage), Performance (<15s), Quality gates | 35-40 hours |
| Phase 4: Deployment | 4-5 | Docker, Monitoring, Security, Launch | 20-25 hours |
| **TOTAL** | **4-5 weeks** | **Full MVP** | **120-145 hours** |

---

## Critical Path Dependencies

```
Phase 1 (Must complete all):
  ├─ Backend infrastructure (blocking all services)
  ├─ Planning agent (blocking diagram generation)
  ├─ Diagram generator (blocking review agent)
  ├─ Review agent (blocking image converter)
  ├─ Image converter (blocking frontend display)
  ├─ File manager (blocking exports)
  ├─ Orchestrator (blocking API endpoint)
  ├─ FastAPI endpoint (blocking frontend communication)
  └─ Frontend UI (can start in parallel with backend)

Phase 2 (Can start after Phase 1):
  ├─ Content filtering (enhances Phase 1)
  ├─ Error handling (improves Phase 1)
  ├─ Logging (improves Phase 1)
  └─ Caching (improves Phase 1 performance)

Phase 3 (Can start after Phase 2):
  ├─ Unit tests (test Phase 1 + 2 code)
  ├─ Integration tests
  ├─ E2E tests
  └─ Performance optimization

Phase 4 (After Phase 3):
  ├─ Docker setup
  ├─ Health checks
  ├─ Deployment
  └─ Launch
```

---

## Parallel Work Tracks

**Can run simultaneously**:
1. **Backend Development** (Phase 1.2-1.9)
2. **Frontend Development** (Phase 1.10) ← Can start early
3. **Environment Setup** (Phase 2.8) ← Can start early
4. **Documentation** (Phase 3.6) ← Can start early

**Suggested approach**:
- Day 1-2: Backend infrastructure + Frontend setup (in parallel)
- Day 3-5: Implement services (planning, generation, review, image conversion)
- Day 6-8: Implement API + integrate frontend
- Day 9-10: Manual testing + error handling
- Week 2+: Testing, optimization, deployment

---

## Success Metrics by Phase

**Phase 1 Complete**: MVP works end-to-end, users can generate diagrams
**Phase 2 Complete**: Production-quality error handling and user experience
**Phase 3 Complete**: 80%+ test coverage, <15s performance, quality gates passing
**Phase 4 Complete**: Deployed to production, monitoring active, ready for users

---

## Next Steps

1. **Approve this roadmap** - Confirm timeline and priorities
2. **Set up repository** - Clone, create branches, add team access
3. **Begin Phase 1** - Start with backend infrastructure (1.1)
4. **Daily standups** - Track progress, identify blockers
5. **Post-phase reviews** - Validate completion before moving forward

