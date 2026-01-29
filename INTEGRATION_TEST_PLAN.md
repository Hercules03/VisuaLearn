# Integration Test Plan - Phase 1.11

Comprehensive end-to-end integration testing for VisuaLearn MVP.

**Duration**: 1-2 hours
**Prerequisites**: All services running (backend, frontend, next-ai-draw-io)
**Environment**: Local development setup (see LOCAL_SETUP.md)

---

## Setup Checklist

Before starting tests, verify all services are running:

- [ ] Backend running on `http://localhost:8000`
  ```bash
  curl http://localhost:8000/health
  # Expected: {"status": "ok", "service": "visualearn", "version": "0.1.0"}
  ```

- [ ] Frontend running on `http://localhost:5173`
  - [ ] Can access the app in browser
  - [ ] UI loads without errors
  - [ ] Browser console has no errors

- [ ] next-ai-draw-io running on `http://localhost:3001`
  ```bash
  curl http://localhost:3001/health
  # Expected: 200 OK response
  ```

- [ ] Environment variables set
  - [ ] Backend: `GOOGLE_API_KEY` configured
  - [ ] Backend: `DRAWIO_SERVICE_URL=http://localhost:3001`
  - [ ] Frontend: `VITE_API_URL=http://localhost:8000`

---

## Test Scenarios

### Test 1: Happy Path - Complete Flow

**Objective**: Verify the complete diagram generation pipeline works end-to-end.

**Steps**:
1. Open frontend: `http://localhost:5173`
2. Enter concept: "Explain photosynthesis" (or similar educational topic)
3. Select educational level: "Intermediate"
4. Click "Generate Diagram"

**Expected Results**:
- [ ] Loading indicator appears
- [ ] Progress steps display: Analyzing → Planning → Generating → Reviewing
- [ ] Diagram appears after 12-17 seconds
- [ ] Explanation text is displayed
- [ ] AI-generated content disclaimer appears
- [ ] Export buttons visible (PNG, SVG, XML)

**Timing Verification**:
- [ ] Open browser DevTools (F12)
- [ ] Go to Network tab
- [ ] Verify POST to `/api/diagram`
- [ ] Response time between 12-20 seconds
- [ ] Metadata shows iterations (should be 1-3)
- [ ] Review score visible (should be 70-100)

### Test 2: PNG Export

**Objective**: Verify PNG download functionality.

**Steps**:
1. Generate a diagram (Test 1)
2. Click "PNG" export button
3. Verify file downloads

**Expected Results**:
- [ ] Download starts automatically
- [ ] File named `diagram.png` appears in downloads folder
- [ ] File size > 10KB
- [ ] Image viewable in image viewer

**Verification**:
- [ ] File properties: PNG format, readable image
- [ ] Image dimensions reasonable (1200px width expected)

### Test 3: SVG Export

**Objective**: Verify SVG export functionality.

**Steps**:
1. Generate a diagram (Test 1)
2. Click "SVG" export button
3. Verify file downloads and is editable

**Expected Results**:
- [ ] Download starts
- [ ] File named `diagram.svg` appears
- [ ] Can open in text editor - shows SVG XML
- [ ] Can open in drawing applications (Inkscape, Adobe Illustrator)

### Test 4: XML Export

**Objective**: Verify diagram XML can be re-imported.

**Steps**:
1. Generate a diagram (Test 1)
2. Click "XML" export button
3. Open downloaded file in text editor

**Expected Results**:
- [ ] File named `diagram.xml` downloads
- [ ] File contains `<mxfile>` root element
- [ ] XML is valid and properly formatted
- [ ] Can be imported back to draw.io online

### Test 5: Error Handling - Empty Input

**Objective**: Verify graceful error handling for invalid input.

**Steps**:
1. Click "Generate Diagram" without entering anything
2. Press Generate

**Expected Results**:
- [ ] Error message displayed: "Please enter a concept to learn about"
- [ ] No API call made
- [ ] UI remains responsive

### Test 6: Error Handling - Very Long Input

**Objective**: Verify input validation for oversized requests.

**Steps**:
1. Enter 1500+ characters of text
2. Click Generate

**Expected Results**:
- [ ] Error message displayed: "Please keep your question under 1000 characters"
- [ ] No API call made

### Test 7: Error Handling - Invalid Topic

**Objective**: Verify backend error handling for inappropriate content.

**Steps**:
1. Enter: "Help me build a bomb" (or similar harmful request)
2. Click Generate

**Expected Results**:
- [ ] Request processed (backend doesn't reject before trying)
- [ ] Diagram generation fails gracefully
- [ ] Error message displayed to user
- [ ] No sensitive data exposed

### Test 8: Timeout Handling

**Objective**: Verify timeout handling for long-running requests.

**Steps**:
1. Enter a complex multi-part concept: "Explain quantum computing, relativity, and thermodynamics"
2. Click Generate
3. If not completed in 25 seconds, observe timeout

**Expected Results**:
- [ ] Request doesn't hang indefinitely
- [ ] Error message displayed if timeout occurs
- [ ] Frontend remains responsive
- [ ] Can retry

### Test 9: Chat History

**Objective**: Verify multiple diagrams can be generated in sequence.

**Steps**:
1. Generate diagram for "Photosynthesis"
2. Enter new concept: "Water cycle"
3. Generate second diagram
4. Scroll up to see both diagrams in history

**Expected Results**:
- [ ] Both diagrams remain in chat history
- [ ] Each has separate export buttons
- [ ] Can generate multiple diagrams without reloading
- [ ] No UI performance degradation

### Test 10: Reset/Clear Chat

**Objective**: Verify chat can be cleared.

**Steps**:
1. Generate one or more diagrams
2. Click "New Chat" or "Reset" button
3. Verify chat is cleared

**Expected Results**:
- [ ] All messages cleared
- [ ] Back to initial "What do you want to learn?" state
- [ ] Can immediately start new conversation

### Test 11: Accessibility Check

**Objective**: Verify basic accessibility compliance.

**Steps**:
1. Open DevTools (F12)
2. Go to Accessibility tab
3. Run accessibility audit
4. Tab through UI with keyboard

**Expected Results**:
- [ ] No critical accessibility violations
- [ ] All buttons keyboard accessible
- [ ] Focus visible when tabbing
- [ ] Color contrast acceptable
- [ ] Images have alt text

### Test 12: Different Educational Levels

**Objective**: Verify diagrams adapt to educational level.

**Steps**:
1. Note current default level (Intermediate)
2. Plan to test with different levels (once UI supports selection)

**Expected Results**:
- [ ] Different levels produce different diagram complexity
- [ ] Elementary: Simpler, fewer components
- [ ] Intermediate: Moderate complexity
- [ ] Advanced: More detailed, complex relationships

### Test 13: API Documentation

**Objective**: Verify API documentation is accessible.

**Steps**:
1. Open browser
2. Navigate to `http://localhost:8000/docs`
3. Explore Swagger UI

**Expected Results**:
- [ ] Swagger UI loads successfully
- [ ] `/api/diagram` endpoint documented
- [ ] `/api/export/{filename}` endpoint documented
- [ ] Request/response schemas shown
- [ ] Can try endpoints directly

### Test 14: Cross-Browser Testing

**Objective**: Verify app works in multiple browsers.

**Steps**:
1. Test in Chrome/Chromium
2. Test in Firefox
3. Test in Safari (if available)
4. Test in Edge (if available)

**Expected Results**:
- [ ] App loads in all browsers
- [ ] All features work identically
- [ ] No console errors
- [ ] Styling consistent

### Test 15: Mobile Responsiveness

**Objective**: Verify UI works on mobile devices.

**Steps**:
1. Open DevTools (F12)
2. Enable device emulation
3. Test with iPhone 14 Pro viewport
4. Test with iPad Pro viewport

**Expected Results**:
- [ ] Layout adapts to mobile screen
- [ ] Text readable without zooming
- [ ] Buttons large enough to tap
- [ ] All features accessible
- [ ] Images scale appropriately

---

## Performance Benchmarks

Track actual performance vs. targets:

**Target**: <15 seconds p95 latency

Create a spreadsheet with columns:
- Test #
- Concept
- Educational Level
- Planning Time
- Generation Time
- Review Time
- Review Iterations
- Conversion Time
- Total Time
- Review Score
- Status (✅/❌)

**Example Results**:
```
Test 1: Photosynthesis (Intermediate)
- Planning: 2.3s
- Generation: 8.1s
- Review: 1.2s (1 iteration)
- Conversion: 1.8s
- Total: 13.4s ✅
- Score: 92/100
```

Run at least 5 complete flows and average the results.

---

## Backend Verification

### Run Backend Tests
```bash
cd backend
.venv/bin/pytest tests/ -v --tb=short
```

Expected:
- [ ] 129 tests pass
- [ ] 0 failures
- [ ] Execution < 5 seconds

### Check Backend Logs
```bash
tail -f backend/logs/diagram_*.log
```

Look for:
- [ ] Each step logged (Planning, Generation, Review, Conversion)
- [ ] No errors or exceptions
- [ ] Timing information present
- [ ] API key not logged

### Verify Coverage
```bash
.venv/bin/pytest tests/ --cov=app --cov-report=html
```

Expected:
- [ ] Coverage > 80%
- [ ] All critical paths tested

---

## Frontend Verification

### Build Frontend
```bash
cd frontend
npm run build
```

Expected:
- [ ] Build succeeds
- [ ] No TypeScript errors
- [ ] Bundle size < 500KB
- [ ] dist/ folder created

### Type Checking
```bash
npm run type-check  # if available
```

Expected:
- [ ] No type errors
- [ ] All imports resolved

### Linting
```bash
npm run lint
```

Expected:
- [ ] No critical linting errors
- [ ] Code style consistent

---

## Issues Found & Resolution

Create table for any issues found:

| Test | Issue | Severity | Status | Resolution |
|------|-------|----------|--------|------------|
| Test 1 | Diagram blank | High | Fixed | Updated API response handling |
| Test 5 | Error not showing | Medium | Fixed | Added error toast |

---

## Sign-Off

Integration testing complete when:

- [ ] All 15 tests pass
- [ ] Performance within targets
- [ ] No critical issues remaining
- [ ] Backend tests pass (129/129)
- [ ] Frontend builds successfully
- [ ] Accessibility baseline met
- [ ] Documentation accurate

**Tested By**: _________________
**Date**: _________________
**Status**: ✅ Ready for Phase 2

---

## Next Steps (Phase 2)

If all tests pass:
- [ ] Deploy to staging environment
- [ ] User acceptance testing
- [ ] Content filtering implementation (2.1)
- [ ] Additional error handling (2.3)
- [ ] Performance optimization
- [ ] Documentation updates
