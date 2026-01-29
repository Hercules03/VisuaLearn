# VisuaLearn Local Development Setup

Complete guide for running VisuaLearn locally for development and testing.

## Prerequisites

- Python 3.11+
- Node.js 20+
- npm 10+
- Google API Key (for Gemini)

## Quick Start (5-10 minutes)

### 1. Set up Backend

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Create .env file
cp .env.example .env

# Edit .env and add your Google API key
# GOOGLE_API_KEY=your_key_here
# DRAWIO_SERVICE_URL=http://localhost:3001
```

### 2. Set up Frontend

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Create .env file
cp .env.example .env
# VITE_API_URL is already set to http://localhost:8000
```

### 3. Set up next-ai-draw-io Service

Option A: Using Docker (recommended)
```bash
docker run -d \
  -p 3001:3001 \
  -e AI_PROVIDER=gemini \
  -e GOOGLE_API_KEY=your_key_here \
  ghcr.io/dayuanjiang/next-ai-draw-io:latest
```

Option B: Running locally (requires Node.js 20)
```bash
# Clone the repository
git clone https://github.com/dayuanjiang/next-ai-draw-io.git
cd next-ai-draw-io

# Install dependencies
npm install

# Create .env
echo "AI_PROVIDER=gemini" > .env
echo "GOOGLE_API_KEY=your_key_here" >> .env

# Start the service
npm start  # or npm run dev for development
```

## Running the Services

Open 3 terminal windows/tabs:

### Terminal 1: Backend

```bash
cd backend
source .venv/bin/activate
python -m uvicorn app.main:app --reload
```

The backend will start at `http://localhost:8000`
- API: `http://localhost:8000/api/diagram`
- Docs: `http://localhost:8000/docs`

### Terminal 2: Frontend

```bash
cd frontend
npm run dev
```

The frontend will start at `http://localhost:5173`
- App: `http://localhost:5173`

### Terminal 3: Next-AI-Draw-io (if running locally)

```bash
cd next-ai-draw-io
npm run dev
```

The service will start at `http://localhost:3001`

## Verify Everything is Running

### Backend Health Check
```bash
curl http://localhost:8000/health
# Expected: {"status": "ok", "service": "visualearn", "version": "0.1.0"}
```

### API Documentation
Visit `http://localhost:8000/docs` to see Swagger UI with all endpoints

### Frontend
Visit `http://localhost:5173` and try generating a diagram

## Testing

### Run Backend Tests
```bash
cd backend
.venv/bin/pytest tests/ -v
```

Expected: 129 tests passing

### Build Frontend
```bash
cd frontend
npm run build
```

Expected: Builds successfully without errors

## Common Issues

### Issue: Backend can't find Gemini API key
**Solution**:
```bash
# Backend
cd backend
echo "GOOGLE_API_KEY=your_actual_key" >> .env
```

### Issue: Frontend can't connect to backend
**Solution**: Ensure backend is running on port 8000
```bash
# Check backend is running
curl http://localhost:8000/health
```

### Issue: next-ai-draw-io service not responding
**Solution**: Restart the service and check logs
```bash
# Check if service is running
curl http://localhost:3001/health

# If using Docker, check logs
docker logs <container_id>
```

### Issue: Port already in use
**Solution**: Change the port in `.env` or kill the process using the port
```bash
# Find process using port 8000
lsof -i :8000
# Kill the process
kill -9 <PID>
```

## Environment Variables

### Backend (.env)
```env
GOOGLE_API_KEY=your_gemini_api_key
DRAWIO_SERVICE_URL=http://localhost:3001
DEBUG=true
LOG_LEVEL=DEBUG
PLANNING_TIMEOUT=5
GENERATION_TIMEOUT=12
REVIEW_TIMEOUT=3
IMAGE_TIMEOUT=4
REVIEW_MAX_ITERATIONS=3
```

### Frontend (.env)
```env
VITE_API_URL=http://localhost:8000
```

## Development Workflow

### Making Changes

**Backend**:
1. Edit code in `backend/app/`
2. Tests auto-run if using `--reload`
3. Verify with: `pytest tests/`

**Frontend**:
1. Edit code in `frontend/src/`
2. Changes auto-reload in browser
3. Check console for errors
4. Build to verify: `npm run build`

### Running Tests Before Commit

```bash
# Backend
cd backend
.venv/bin/pytest tests/ --cov=app --cov-report=term-missing

# Frontend (lint only - no tests yet)
cd frontend
npm run lint
```

## API Testing with curl

### Generate a Diagram
```bash
curl -X POST http://localhost:8000/api/diagram \
  -H "Content-Type: application/json" \
  -d '{
    "concept": "Explain photosynthesis",
    "educational_level": "intermediate"
  }'
```

### Download File
```bash
curl -X GET http://localhost:8000/api/export/{filename} \
  -o diagram.png
```

## Docker Setup (Alternative)

If you prefer using Docker:

```bash
# Ensure GOOGLE_API_KEY is set
export GOOGLE_API_KEY=your_key_here

# Run all services
docker-compose up

# In another terminal, run tests
docker-compose exec backend pytest tests/

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f next-ai-draw-io
```

## Troubleshooting

### View logs

**Backend**:
```bash
# Logs are in backend/logs/diagram_*.log
tail -f backend/logs/diagram_*.log
```

**Frontend**: Check browser console (F12)

**next-ai-draw-io**: Check terminal output

### Debug mode

**Backend**:
- Set `DEBUG=true` in .env
- Set `LOG_LEVEL=DEBUG` in .env
- Logs will include detailed information

**Frontend**:
- Open DevTools (F12)
- Check Network tab for API calls
- Check Console for errors

## Performance Baseline

Expected timing for a typical request:
- Planning: 2-3 seconds
- Generation: 8-10 seconds
- Review: 1-2 seconds
- Image conversion: 1-2 seconds
- **Total: 12-17 seconds**

If requests are taking longer, check:
- API rate limiting (Google Gemini API)
- Network latency
- System resources (CPU, memory)

## Next Steps

Once everything is running:

1. **Test the UI**: http://localhost:5173
   - Try "Explain photosynthesis"
   - Verify diagram displays
   - Test PNG/SVG/XML downloads

2. **Run full test suite**: `cd backend && pytest tests/`

3. **Check API docs**: http://localhost:8000/docs

4. **Review logs**: `backend/logs/diagram_*.log`

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Google Gemini API](https://ai.google.dev/)
- [next-ai-draw-io Repository](https://github.com/dayuanjiang/next-ai-draw-io)
