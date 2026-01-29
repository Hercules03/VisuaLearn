# VisuaLearn Quick Start Guide

Get VisuaLearn running locally in 5-10 minutes.

## Prerequisites

- Python 3.11+
- Node.js 20+
- Google Gemini API Key (get one free at [ai.google.dev](https://ai.google.dev))

## Step 1: Start Backend (2 minutes)

```bash
# Navigate to backend
cd backend

# Create Python environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
playwright install chromium

# Create .env with your API key
cp .env.example .env
# Edit .env and add: GOOGLE_API_KEY=your_key_here
# Also set: DRAWIO_SERVICE_URL=http://localhost:3001

# Start backend (press Ctrl+C to stop)
python -m uvicorn app.main:app --reload
```

✅ Backend running on http://localhost:8000

## Step 2: Start Frontend (1 minute)

**In a new terminal:**

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Create .env (optional - uses default http://localhost:8000)
cp .env.example .env

# Start development server (press Ctrl+C to stop)
npm run dev
```

✅ Frontend running on http://localhost:5173

## Step 3: Start Diagram Service (1 minute)

**In a new terminal:**

```bash
# Option A: Using Docker (recommended)
docker run -d -p 3001:3001 \
  -e AI_PROVIDER=gemini \
  -e GOOGLE_API_KEY=your_key_here \
  ghcr.io/dayuanjiang/next-ai-draw-io:latest

# Option B: Using Node.js
# git clone https://github.com/dayuanjiang/next-ai-draw-io.git
# cd next-ai-draw-io
# npm install
# echo "AI_PROVIDER=gemini" > .env
# echo "GOOGLE_API_KEY=your_key_here" >> .env
# npm start
```

✅ Service running on http://localhost:3001

## Step 4: Test It! (1 minute)

1. Open http://localhost:5173 in your browser
2. Type: "Explain photosynthesis"
3. Click "Generate Diagram"
4. Wait 12-17 seconds ⏳
5. See your diagram! 🎉

## Verify Everything

```bash
# Check backend is running
curl http://localhost:8000/health

# Check frontend builds
cd frontend && npm run build

# Run backend tests
cd backend && .venv/bin/pytest tests/ -q
# Expected: 129 passed
```

## Troubleshooting

**"Connection refused on port 8000"**
→ Make sure backend is running: `python -m uvicorn app.main:app --reload`

**"Cannot find module"**
→ Install dependencies: `npm install` or `pip install -r requirements.txt`

**"API key error"**
→ Check .env files have GOOGLE_API_KEY set

**"Diagram is blank"**
→ Check browser console (F12) for errors
→ Check backend logs

## What Next?

- **See Architecture**: Read `PHASE_1_SUMMARY.md`
- **Setup Locally**: See `LOCAL_SETUP.md`
- **Run Integration Tests**: See `INTEGRATION_TEST_PLAN.md`
- **API Docs**: Visit http://localhost:8000/docs

## File Structure

```
visuaLearn/
├── backend/          # FastAPI server
│   ├── app/          # Services, models, API
│   └── tests/        # 129 unit + integration tests
├── frontend/         # React + Vite
│   └── src/          # Components, hooks, API client
└── docs/            # Documentation
```

## Quick Commands

```bash
# Backend
cd backend
python -m uvicorn app.main:app --reload  # Start with hot reload
.venv/bin/pytest tests/ -v                # Run all tests
.venv/bin/pytest tests/services/ -v       # Run service tests
.venv/bin/pytest tests/api/ -v            # Run API tests

# Frontend
cd frontend
npm run dev       # Start dev server
npm run build     # Production build
npm run lint      # Run linter

# Run all in one (separate terminals)
# Terminal 1: cd backend && python -m uvicorn app.main:app --reload
# Terminal 2: cd frontend && npm run dev
# Terminal 3: docker run ... (next-ai-draw-io)
```

## System Requirements

- **RAM**: 2GB minimum
- **Disk**: 1GB minimum
- **Network**: Stable internet (API calls to Google)

## Performance

- **Planning**: 2-3s
- **Generation**: 8-10s
- **Review**: 1-2s
- **Conversion**: 1-2s
- **Total**: 12-17s

If slower, check:
- Network connection
- System resources
- API rate limits

## Environment Variables

**Backend (.env)**:
```env
GOOGLE_API_KEY=your_gemini_api_key
DRAWIO_SERVICE_URL=http://localhost:3001
DEBUG=true
LOG_LEVEL=DEBUG
```

**Frontend (.env)**:
```env
VITE_API_URL=http://localhost:8000
```

## Need Help?

1. Check LOCAL_SETUP.md for detailed setup
2. Check INTEGRATION_TEST_PLAN.md for testing issues
3. Look at logs:
   - Backend: `backend/logs/diagram_*.log`
   - Frontend: Browser console (F12)
3. Review PHASE_1_SUMMARY.md for architecture

---

**Happy developing! 🚀**

For full documentation, see:
- `LOCAL_SETUP.md` - Detailed setup guide
- `INTEGRATION_TEST_PLAN.md` - Testing guide
- `PHASE_1_SUMMARY.md` - Technical overview
