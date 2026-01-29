"""Shared pytest fixtures and configuration."""

import asyncio
import os
import sys
from unittest.mock import AsyncMock, MagicMock

import pytest


@pytest.fixture
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_gemini_response():
    """Mock Gemini API response for planning agent."""
    return {
        "concept": "Photosynthesis",
        "diagram_type": "flowchart",
        "components": [
            "Sunlight",
            "Water",
            "Carbon Dioxide",
            "Glucose",
            "Oxygen",
        ],
        "relationships": [
            {
                "from": "Sunlight",
                "to": "Energy",
                "label": "provides",
            },
            {
                "from": "Water",
                "to": "Glucose",
                "label": "converted to",
            },
        ],
        "success_criteria": [
            "All inputs present",
            "Clear output shown",
            "Energy flow visible",
        ],
        "educational_level": "11-13",
        "key_insights": ["Plants make their own food", "Sunlight is energy source"],
    }


@pytest.fixture
def mock_drawio_xml():
    """Mock draw.io XML response."""
    return """<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="app.diagrams.net" modified="2024-01-28T12:00:00.000Z" version="20.8.0">
  <diagram id="diagram1" name="Page-1">
    <mxGraphModel dx="1200" dy="800" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="827" pageHeight="1169">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        <mxCell id="c1" value="Photosynthesis" style="rounded=1;whiteSpace=wrap;html=1;" vertex="1" parent="1">
          <mxGeometry x="10" y="10" width="120" height="60" as="geometry"/>
        </mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>"""


@pytest.fixture
def mock_png_bytes():
    """Mock PNG image bytes."""
    # Simple 1x1 transparent PNG
    return b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"


@pytest.fixture
def mock_gemini_client(mock_gemini_response):
    """Mock Google Generative AI client."""
    client = AsyncMock()
    client.generate_content = AsyncMock(
        return_value=MagicMock(text=str(mock_gemini_response))
    )
    return client


@pytest.fixture
def mock_playwright_browser(mock_png_bytes):
    """Mock Playwright browser."""
    browser = AsyncMock()
    page = AsyncMock()

    # Mock page screenshot
    page.screenshot = AsyncMock(return_value=mock_png_bytes)
    page.close = AsyncMock()

    # Mock browser context and page
    context = AsyncMock()
    context.new_page = AsyncMock(return_value=page)
    context.close = AsyncMock()

    browser.new_context = AsyncMock(return_value=context)
    browser.close = AsyncMock()

    return browser


@pytest.fixture
def mock_httpx_client(mock_drawio_xml):
    """Mock httpx HTTP client for API calls."""
    client = AsyncMock()
    response = AsyncMock()
    response.status_code = 200
    response.text = mock_drawio_xml
    response.json = AsyncMock(return_value={"xml": mock_drawio_xml})

    client.post = AsyncMock(return_value=response)
    client.get = AsyncMock(return_value=response)

    return client


@pytest.fixture(autouse=True)
def mock_google_generativeai(monkeypatch):
    """Auto-mock google.generativeai module for all tests."""
    # Create mock for google.generativeai
    mock_genai = MagicMock()
    mock_genai.GenerativeModel = MagicMock()
    mock_genai.configure = MagicMock()

    # Add to sys.modules so imports work
    sys.modules["google"] = MagicMock()
    sys.modules["google.generativeai"] = mock_genai

    yield mock_genai

    # Cleanup
    if "google.generativeai" in sys.modules:
        del sys.modules["google.generativeai"]
    if "google" in sys.modules:
        del sys.modules["google"]


@pytest.fixture
def test_env(tmp_path, monkeypatch):
    """Create test environment with temporary directory."""
    env_vars = {
        "GOOGLE_API_KEY": "test-key-123",
        "DRAWIO_SERVICE_URL": "http://localhost:3001",
        "DEBUG": "true",
        "LOG_LEVEL": "DEBUG",
        "PLANNING_TIMEOUT": "5",
        "GENERATION_TIMEOUT": "12",
        "REVIEW_TIMEOUT": "3",
        "IMAGE_TIMEOUT": "4",
        "REVIEW_MAX_ITERATIONS": "3",
        "TEMP_DIR": str(tmp_path / "temp"),
        "TEMP_FILE_TTL": "3600",
        "CLEANUP_INTERVAL": "600",
        "CACHE_SIZE_MB": "500",
        "CACHE_TTL_SECONDS": "3600",
    }

    # Set environment variables
    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)

    # Create temp directory
    (tmp_path / "temp").mkdir(exist_ok=True)

    return env_vars, tmp_path
