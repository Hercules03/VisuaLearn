# VisuaLearn Backend

FastAPI backend for AI-powered educational diagram generation.

## Quick Start

### 1. Setup Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your Google API key
# GOOGLE_API_KEY=your_key_here
# DRAWIO_SERVICE_URL=http://localhost:3001
```

### 2. Install Dependencies

Dependencies are already installed with `uv sync`. If you need to reinstall:

```bash
uv sync --python 3.11
```

### 3. Install Playwright Browsers

```bash
.venv/bin/playwright install chromium
```

### 4. Run Backend

```bash
# Using uvicorn directly
.venv/bin/uvicorn app.main:app --reload

# Or using Python
python -m uvicorn app.main:app --reload
```

Server will start at `http://localhost:8000`

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Settings from environment
│   ├── errors.py            # Custom exceptions
│   ├── api/
│   │   ├── __init__.py
│   │   └── diagram.py       # Diagram endpoints (TODO)
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py       # Pydantic models
│   └── services/
│       ├── __init__.py
│       ├── orchestrator.py       # Pipeline coordinator (TODO)
│       ├── planning_agent.py      # Planning agent (TODO)
│       ├── review_agent.py        # Review agent (TODO)
│       ├── image_converter.py     # Image rendering (TODO)
│       └── file_manager.py        # File operations (TODO)
├── tests/                   # Test directory
├── temp/                    # Temporary files (auto-cleanup)
├── logs/                    # Application logs
├── .env.example             # Environment template
├── .gitignore               # Git ignore patterns
├── pyproject.toml           # Project configuration
└── README.md                # This file
```

## Environment Variables

Copy `.env.example` to `.env` and fill in required values:

```env
# Required
GOOGLE_API_KEY=your_google_api_key_here
DRAWIO_SERVICE_URL=http://localhost:3001

# Optional (defaults provided)
DEBUG=true
LOG_LEVEL=DEBUG
PLANNING_TIMEOUT=5
GENERATION_TIMEOUT=12
REVIEW_TIMEOUT=3
IMAGE_TIMEOUT=4
REVIEW_MAX_ITERATIONS=3
```

See `.env.example` for all available settings.

## API Endpoints

### Health Check

```bash
curl http://localhost:8000/health
```

### Generate Diagram (TODO)

```bash
curl -X POST http://localhost:8000/api/diagram \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "Explain photosynthesis",
    "language": "en"
  }'
```

### Download Export (TODO)

```bash
curl http://localhost:8000/api/export/filename.png -o diagram.png
```

## Development

### Running Tests

```bash
# Run all tests
.venv/bin/pytest tests/ -v

# Run with coverage
.venv/bin/pytest tests/ --cov=app --cov-report=term-missing

# Run specific test file
.venv/bin/pytest tests/test_models.py -v

# Watch mode (auto-run on changes)
.venv/bin/pytest-watch tests/
```

### Type Checking

```bash
.venv/bin/mypy app/
```

### Linting

```bash
.venv/bin/ruff check app/
```

### Code Formatting

```bash
.venv/bin/black app/ tests/
```

### Quality Gates (Run All Checks)

```bash
# Run all quality checks
.venv/bin/pytest tests/ --cov=app && \
.venv/bin/mypy app/ && \
.venv/bin/ruff check app/ && \
.venv/bin/black --check app/
```

## Architecture

See `../claude.md` for detailed architecture and guidelines.

### Agent Pipeline

```
User Input
    ↓
Planning Agent (3s target, 5s max)
    ↓
Diagram Generator (8s target, 12s max)
    ↓
Review Agent (2s target, 3s max per iteration)
    ↓
Image Converter (2s target, 4s max)
    ↓
Response (15s target, 20s max)
```

## Logging

Logs are written to:
- **Console**: Debug/INFO level messages
- **File**: `logs/diagram_{timestamp}.log` - all messages

Configure in `app/main.py`:

```python
logger.add(
    sys.stderr,
    format="...",
    level=settings.log_level,
)
logger.add("logs/diagram_{time}.log", rotation="500 MB")
```

## Troubleshooting

### "ImportError: No module named 'google'"

Ensure dependencies are installed:
```bash
uv sync
```

### "GOOGLE_API_KEY not found"

Create `.env` file with your API key:
```bash
cp .env.example .env
# Edit .env and add your key
```

### Playwright installation fails

Try manual installation:
```bash
.venv/bin/playwright install --with-deps chromium
```

### Port 8000 already in use

Use a different port:
```bash
.venv/bin/uvicorn app.main:app --port 8001
```

## Deployment

For deployment instructions, see `../ROADMAP.md` Phase 4.

## Contributing

1. Create feature branch
2. Run tests and quality gates
3. Submit PR with clear description

See `../claude.md` for detailed development guidelines.

## License

See LICENSE file in project root.
