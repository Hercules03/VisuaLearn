# Simplified FastAPI Implementation - Stateless MVP
## AI-Powered Educational Diagram Tool (No Auth, No Database)

This is a minimal implementation focusing on core diagram generation functionality.

## Key Simplifications

✅ **No Database** - Everything in memory/temp files  
✅ **No Authentication** - Open API  
✅ **No User Management** - Stateless sessions  
✅ **No Redis** - Simple file-based temp storage  
✅ **No Complex Storage** - Local temp directory with auto-cleanup  
✅ **Auto-Cleanup** - Files deleted after 1 hour  

## Project Structure

```
backend/
├── app/
│   ├── main.py                 # FastAPI entry point
│   ├── config.py               # Settings
│   ├── api/
│   │   └── diagram.py          # API endpoints
│   ├── models/
│   │   └── schemas.py          # Pydantic models
│   └── services/
│       ├── orchestrator.py     # Main pipeline
│       ├── planning_agent.py   # Educational planning
│       ├── diagram_generator.py# Draw.io XML generation
│       ├── review_agent.py     # Quality review
│       ├── image_converter.py  # XML to PNG
│       ├── xml_parser.py       # Parse diagrams
│       └── file_manager.py     # Temp file handling
├── temp/                       # Auto-cleaned temporary files
├── requirements.txt
└── docker-compose.yml
```

See FASTAPI_IMPLEMENTATION.md for detailed service implementations.

## Quick Start

### 1. Install Dependencies

```bash
pip install fastapi uvicorn anthropic playwright httpx pydantic pydantic-settings lxml loguru python-dotenv pillow
playwright install chromium
```

### 2. Create .env

```bash
ANTHROPIC_API_KEY=your_key_here
DRAWIO_SERVICE_URL=http://localhost:3001
DEBUG=true
```

### 3. Run

```bash
# Terminal 1: Start next-ai-draw-io
docker run -p 3001:3000 \
  -e AI_PROVIDER=anthropic \
  -e ANTHROPIC_API_KEY=your_key \
  ghcr.io/dayuanjiang/next-ai-draw-io:latest

# Terminal 2: Start FastAPI
uvicorn app.main:app --reload
```

### 4. Test

```bash
curl -X POST http://localhost:8000/api/diagram \
  -H "Content-Type: application/json" \
  -d '{"user_input":"Explain photosynthesis","language":"en"}'
```

## API Reference

### POST /api/diagram

Generate diagram from concept.

**Request:**
```json
{
  "user_input": "Explain how HTTP works",
  "language": "en"
}
```

**Response:**
```json
{
  "explanation": "HTTP is a protocol...",
  "diagram_image": "data:image/png;base64,...",
  "diagram_xml": "<mxfile>...</mxfile>",
  "export_urls": {
    "png": "/api/export/temp_123.png",
    "svg": "/api/export/temp_123.svg",
    "xml": "/api/export/temp_123.xml"
  },
  "metadata": {
    "iterations": 2,
    "approved": true,
    "score": 92.5,
    "generation_time": 12.3
  }
}
```

### GET /api/export/{filename}

Download exported file (PNG/SVG/XML).

**Auto-deletion:** Files are automatically removed after 1 hour.

