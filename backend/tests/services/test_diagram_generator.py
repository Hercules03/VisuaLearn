"""Tests for Diagram Generator service."""

import asyncio
import json

import pytest

from app.errors import GenerationError
from app.services.diagram_generator import DiagramGenerator
from app.services.planning_agent import PlanningOutput


class TestDiagramGeneratorInit:
    """Test DiagramGenerator initialization."""

    def test_init_creates_generator(self, test_env):
        """Test successful initialization creates generator."""
        generator = DiagramGenerator()
        assert generator.timeout == 12
        assert generator.drawio_url == "http://localhost:3001"


class TestDiagramGeneratorGenerate:
    """Test DiagramGenerator.generate() method."""

    @pytest.mark.asyncio
    async def test_generate_http_timeout(self, test_env, monkeypatch):
        """Test generate with HTTP timeout."""

        async def slow_post(*args, **kwargs):
            await asyncio.sleep(10)

        class MockClient:
            async def post(self, *args, **kwargs):
                return await slow_post()

            async def __aenter__(self):
                return self

            async def __aexit__(self, *args):
                pass

        def mock_async_client(*args, **kwargs):
            return MockClient()

        monkeypatch.setattr(
            "app.services.diagram_generator.httpx.AsyncClient",
            mock_async_client,
        )

        generator = DiagramGenerator()
        generator.timeout = 0.001  # Set very short timeout

        plan = PlanningOutput(
            concept="Test",
            diagram_type="flowchart",
            components=["A"],
            relationships=[],
            success_criteria=["Test"],
            educational_level="11-13",
            key_insights=["Test"],
        )

        with pytest.raises(GenerationError, match="timed out"):
            await generator.generate(plan)

    @pytest.mark.asyncio
    async def test_generate_timeout(self, test_env, monkeypatch):
        """Test generate raises timeout error."""

        # Mock the _generate_internal to be slow
        async def slow_generation(*args, **kwargs):
            await asyncio.sleep(10)

        generator = DiagramGenerator()
        generator.timeout = 0.001  # Set very short timeout
        generator._generate_internal = slow_generation

        plan = PlanningOutput(
            concept="Test",
            diagram_type="flowchart",
            components=["A"],
            relationships=[],
            success_criteria=["Test"],
            educational_level="11-13",
            key_insights=["Test"],
        )

        with pytest.raises(GenerationError):
            await generator.generate(plan)

    @pytest.mark.asyncio
    async def test_generate_connection_error(self, test_env, monkeypatch):
        """Test generate with connection error."""
        import httpx

        # Mock httpx.AsyncClient to raise ConnectError
        async def mock_post(*args, **kwargs):
            raise httpx.ConnectError("Connection failed")

        class MockClient:
            async def post(self, *args, **kwargs):
                return await mock_post()

            async def __aenter__(self):
                return self

            async def __aexit__(self, *args):
                pass

        def mock_async_client(*args, **kwargs):
            return MockClient()

        monkeypatch.setattr(
            "app.services.diagram_generator.httpx.AsyncClient",
            mock_async_client,
        )

        generator = DiagramGenerator()
        plan = PlanningOutput(
            concept="Test",
            diagram_type="flowchart",
            components=["A"],
            relationships=[],
            success_criteria=["Test"],
            educational_level="11-13",
            key_insights=["Test"],
        )

        with pytest.raises(GenerationError, match="Cannot connect"):
            await generator.generate(plan)

    @pytest.mark.asyncio
    async def test_generate_http_error(self, test_env, monkeypatch):
        """Test generate with HTTP error response."""

        class MockResponse:
            def __init__(self):
                self.status_code = 500
                self.text = "Internal Server Error"

        async def mock_post(*args, **kwargs):
            return MockResponse()

        class MockClient:
            async def post(self, *args, **kwargs):
                return await mock_post()

            async def __aenter__(self):
                return self

            async def __aexit__(self, *args):
                pass

        monkeypatch.setattr(
            "app.services.diagram_generator.httpx.AsyncClient",
            lambda *args, **kwargs: MockClient(),
        )

        generator = DiagramGenerator()
        plan = PlanningOutput(
            concept="Test",
            diagram_type="flowchart",
            components=["A"],
            relationships=[],
            success_criteria=["Test"],
            educational_level="11-13",
            key_insights=["Test"],
        )

        with pytest.raises(GenerationError, match="returned 500"):
            await generator.generate(plan)

    @pytest.mark.asyncio
    async def test_generate_invalid_json_response(self, test_env, monkeypatch):
        """Test generate with invalid JSON response."""

        class MockResponse:
            def __init__(self):
                self.status_code = 200
                self.text = "Not valid JSON"

            def json(self):
                raise json.JSONDecodeError("Invalid JSON", "", 0)

        async def mock_post(*args, **kwargs):
            return MockResponse()

        class MockClient:
            async def post(self, *args, **kwargs):
                return await mock_post()

            async def __aenter__(self):
                return self

            async def __aexit__(self, *args):
                pass

        monkeypatch.setattr(
            "app.services.diagram_generator.httpx.AsyncClient",
            lambda *args, **kwargs: MockClient(),
        )

        generator = DiagramGenerator()
        plan = PlanningOutput(
            concept="Test",
            diagram_type="flowchart",
            components=["A"],
            relationships=[],
            success_criteria=["Test"],
            educational_level="11-13",
            key_insights=["Test"],
        )

        with pytest.raises(GenerationError, match="Invalid JSON"):
            await generator.generate(plan)

    @pytest.mark.asyncio
    async def test_generate_missing_xml_in_response(self, test_env, monkeypatch):
        """Test generate with missing XML in response."""

        class MockResponse:
            def __init__(self):
                self.status_code = 200
                self.text = "{}"

            def json(self):
                return {}  # No 'xml' or 'content' key

        async def mock_post(*args, **kwargs):
            return MockResponse()

        class MockClient:
            async def post(self, *args, **kwargs):
                return await mock_post()

            async def __aenter__(self):
                return self

            async def __aexit__(self, *args):
                pass

        monkeypatch.setattr(
            "app.services.diagram_generator.httpx.AsyncClient",
            lambda *args, **kwargs: MockClient(),
        )

        generator = DiagramGenerator()
        plan = PlanningOutput(
            concept="Test",
            diagram_type="flowchart",
            components=["A"],
            relationships=[],
            success_criteria=["Test"],
            educational_level="11-13",
            key_insights=["Test"],
        )

        with pytest.raises(GenerationError, match="No XML content"):
            await generator.generate(plan)

    @pytest.mark.asyncio
    async def test_generate_invalid_xml_format(self, test_env, monkeypatch):
        """Test generate with invalid XML format."""

        class MockResponse:
            def __init__(self):
                self.status_code = 200
                self.text = '{"xml": "not xml"}'

            def json(self):
                return {"xml": "not xml"}

        async def mock_post(*args, **kwargs):
            return MockResponse()

        class MockClient:
            async def post(self, *args, **kwargs):
                return await mock_post()

            async def __aenter__(self):
                return self

            async def __aexit__(self, *args):
                pass

        monkeypatch.setattr(
            "app.services.diagram_generator.httpx.AsyncClient",
            lambda *args, **kwargs: MockClient(),
        )

        generator = DiagramGenerator()
        plan = PlanningOutput(
            concept="Test",
            diagram_type="flowchart",
            components=["A"],
            relationships=[],
            success_criteria=["Test"],
            educational_level="11-13",
            key_insights=["Test"],
        )

        with pytest.raises(GenerationError, match="valid XML"):
            await generator.generate(plan)


class TestDiagramGeneratorSuccess:
    """Test successful diagram generation."""

    @pytest.mark.asyncio
    async def test_generate_success_with_xml_key(self, test_env, monkeypatch):
        """Test successful generation with 'xml' key in response."""
        valid_xml = "<mxfile><diagram>Test</diagram></mxfile>"

        class MockResponse:
            def __init__(self):
                self.status_code = 200
                self.text = json.dumps({"xml": valid_xml})

            def json(self):
                return {"xml": valid_xml}

        async def mock_post(*args, **kwargs):
            return MockResponse()

        class MockClient:
            async def post(self, *args, **kwargs):
                return await mock_post()

            async def __aenter__(self):
                return self

            async def __aexit__(self, *args):
                pass

        monkeypatch.setattr(
            "app.services.diagram_generator.httpx.AsyncClient",
            lambda *args, **kwargs: MockClient(),
        )

        generator = DiagramGenerator()
        plan = PlanningOutput(
            concept="Test",
            diagram_type="flowchart",
            components=["A"],
            relationships=[],
            success_criteria=["Test"],
            educational_level="11-13",
            key_insights=["Test"],
        )

        result = await generator.generate(plan)
        assert result == valid_xml

    @pytest.mark.asyncio
    async def test_generate_success_with_content_key(self, test_env, monkeypatch):
        """Test successful generation with 'content' key in response."""
        valid_xml = "<mxfile><diagram>Test</diagram></mxfile>"

        class MockResponse:
            def __init__(self):
                self.status_code = 200
                self.text = json.dumps({"content": valid_xml})

            def json(self):
                return {"content": valid_xml}

        async def mock_post(*args, **kwargs):
            return MockResponse()

        class MockClient:
            async def post(self, *args, **kwargs):
                return await mock_post()

            async def __aenter__(self):
                return self

            async def __aexit__(self, *args):
                pass

        monkeypatch.setattr(
            "app.services.diagram_generator.httpx.AsyncClient",
            lambda *args, **kwargs: MockClient(),
        )

        generator = DiagramGenerator()
        plan = PlanningOutput(
            concept="Test",
            diagram_type="flowchart",
            components=["A"],
            relationships=[],
            success_criteria=["Test"],
            educational_level="11-13",
            key_insights=["Test"],
        )

        result = await generator.generate(plan)
        assert result == valid_xml

    @pytest.mark.asyncio
    async def test_generate_with_complex_plan(self, test_env, monkeypatch):
        """Test generation with complex planning output."""
        valid_xml = "<mxfile><diagram>Complex</diagram></mxfile>"

        class MockResponse:
            def __init__(self):
                self.status_code = 200
                self.text = json.dumps({"xml": valid_xml})

            def json(self):
                return {"xml": valid_xml}

        async def mock_post(*args, **kwargs):
            return MockResponse()

        class MockClient:
            async def post(self, *args, **kwargs):
                return await mock_post()

            async def __aenter__(self):
                return self

            async def __aexit__(self, *args):
                pass

        monkeypatch.setattr(
            "app.services.diagram_generator.httpx.AsyncClient",
            lambda *args, **kwargs: MockClient(),
        )

        generator = DiagramGenerator()
        plan = PlanningOutput(
            concept="Photosynthesis",
            diagram_type="flowchart",
            components=["Sunlight", "Water", "CO2", "Glucose"],
            relationships=[
                {"from": "Sunlight", "to": "Energy", "label": "provides"},
                {"from": "Water", "to": "Glucose", "label": "converted"},
            ],
            success_criteria=["All inputs present", "Clear output"],
            educational_level="11-13",
            key_insights=["Plants make food", "Sunlight is energy source"],
        )

        result = await generator.generate(plan)
        assert result == valid_xml


class TestDiagramGeneratorIntegration:
    """Integration tests for Diagram Generator."""

    @pytest.mark.asyncio
    async def test_error_handling_cascade(self, test_env, monkeypatch):
        """Test error is properly caught and re-raised as GenerationError."""

        # Mock httpx.AsyncClient to raise generic exception
        async def mock_post(*args, **kwargs):
            raise RuntimeError("Unexpected error")

        class MockClient:
            async def post(self, *args, **kwargs):
                return await mock_post()

            async def __aenter__(self):
                return self

            async def __aexit__(self, *args):
                pass

        def mock_async_client(*args, **kwargs):
            return MockClient()

        monkeypatch.setattr(
            "app.services.diagram_generator.httpx.AsyncClient",
            mock_async_client,
        )

        generator = DiagramGenerator()
        plan = PlanningOutput(
            concept="Test",
            diagram_type="flowchart",
            components=["A"],
            relationships=[],
            success_criteria=["Test"],
            educational_level="11-13",
            key_insights=["Test"],
        )

        with pytest.raises(GenerationError, match="Unexpected error"):
            await generator.generate(plan)
