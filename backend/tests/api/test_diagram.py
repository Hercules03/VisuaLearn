"""Tests for diagram generation API endpoint."""


import pytest
from fastapi.testclient import TestClient

from app.errors import OrchestrationError
from app.main import app
from app.services.orchestrator import OrchestrationResult
from app.services.planning_agent import PlanningOutput


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestDiagramEndpointValidation:
    """Test request validation."""

    def test_missing_concept(self, client):
        """Test request without concept fails."""
        response = client.post(
            "/api/diagram",
            json={"educational_level": "11-13"},
        )
        assert response.status_code == 422

    def test_missing_educational_level(self, client):
        """Test request without educational_level fails."""
        response = client.post(
            "/api/diagram",
            json={"concept": "Test"},
        )
        assert response.status_code == 422

    def test_invalid_educational_level(self, client):
        """Test request with invalid educational_level fails."""
        response = client.post(
            "/api/diagram",
            json={"concept": "Test", "educational_level": "invalid"},
        )
        assert response.status_code == 422

    def test_valid_educational_levels(self, client, monkeypatch):
        """Test all valid educational levels are accepted."""

        async def mock_orchestrate(*args, **kwargs):
            plan = PlanningOutput(
                concept="Test",
                diagram_type="flowchart",
                components=["A"],
                relationships=[],
                success_criteria=["Test"],
                educational_level="11-13",
                key_insights=["Test"],
            )
            return OrchestrationResult(
                png_filename="test.png",
                svg_filename="test.svg",
                xml_content="<mxfile></mxfile>",
                plan=plan,
                review_score=90,
                iterations=1,
                total_time_seconds=5.0,
                metadata={
                    "step_times": {
                        "planning": 1.0,
                        "generation": 1.0,
                        "review": 1.0,
                        "conversion": 1.0,
                        "storage": 1.0,
                    },
                    "refinement_instructions": [],
                    "concept": "Test",
                    "components_count": 1,
                    "relationships_count": 0,
                },
            )

        from app.api.diagram import orchestrator

        monkeypatch.setattr(orchestrator, "orchestrate", mock_orchestrate)

        for level in ["8-10", "11-13", "14-15"]:
            response = client.post(
                "/api/diagram",
                json={"concept": "Test", "educational_level": level},
            )
            assert response.status_code == 200

    def test_concept_too_long(self, client):
        """Test request with concept exceeding max length fails."""
        response = client.post(
            "/api/diagram",
            json={
                "concept": "x" * 1001,
                "educational_level": "11-13",
            },
        )
        assert response.status_code == 422

    def test_concept_empty(self, client):
        """Test request with empty concept fails."""
        response = client.post(
            "/api/diagram",
            json={"concept": "", "educational_level": "11-13"},
        )
        assert response.status_code == 422


class TestDiagramEndpointSuccess:
    """Test successful diagram generation."""

    @pytest.mark.asyncio
    async def test_diagram_generation_success(self, client, monkeypatch):
        """Test successful diagram generation."""

        plan = PlanningOutput(
            concept="Photosynthesis",
            diagram_type="flowchart",
            components=["Sunlight", "Water", "CO2", "Glucose"],
            relationships=[
                {"from": "Sunlight", "to": "Energy"},
                {"from": "Water", "to": "Glucose"},
            ],
            success_criteria=["All inputs present"],
            educational_level="11-13",
            key_insights=["Plants make food"],
        )

        async def mock_orchestrate(concept, educational_level):
            return OrchestrationResult(
                png_filename="photosynthesis.png",
                svg_filename="photosynthesis.svg",
                xml_content="<mxfile><diagram>Photosynthesis</diagram></mxfile>",
                plan=plan,
                review_score=95,
                iterations=1,
                total_time_seconds=8.5,
                metadata={
                    "step_times": {
                        "planning": 1.0,
                        "generation": 2.0,
                        "review": 1.5,
                        "conversion": 2.0,
                        "storage": 2.0,
                    },
                    "refinement_instructions": [],
                    "concept": "Photosynthesis",
                    "components_count": 4,
                    "relationships_count": 2,
                },
            )

        from app.api.diagram import orchestrator

        monkeypatch.setattr(orchestrator, "orchestrate", mock_orchestrate)

        response = client.post(
            "/api/diagram",
            json={"concept": "Photosynthesis", "educational_level": "11-13"},
        )

        assert response.status_code == 200
        data = response.json()

        assert data["png_filename"] == "photosynthesis.png"
        assert data["svg_filename"] == "photosynthesis.svg"
        assert "Photosynthesis" in data["xml_content"]
        assert data["review_score"] == 95
        assert data["iterations"] == 1
        assert data["total_time_seconds"] == 8.5
        assert data["plan"]["concept"] == "Photosynthesis"
        assert data["plan"]["diagram_type"] == "flowchart"
        assert len(data["plan"]["components"]) == 4
        assert data["metadata"]["components_count"] == 4
        assert data["metadata"]["relationships_count"] == 2

    @pytest.mark.asyncio
    async def test_diagram_response_structure(self, client, monkeypatch):
        """Test response structure matches specification."""

        plan = PlanningOutput(
            concept="Test",
            diagram_type="mindmap",
            components=["A", "B"],
            relationships=[{"from": "A", "to": "B"}],
            success_criteria=["Test"],
            educational_level="14-15",
            key_insights=["Insight"],
        )

        async def mock_orchestrate(concept, educational_level):
            return OrchestrationResult(
                png_filename="test.png",
                svg_filename="test.svg",
                xml_content="<mxfile></mxfile>",
                plan=plan,
                review_score=85,
                iterations=2,
                total_time_seconds=10.0,
                metadata={
                    "step_times": {
                        "planning": 2.0,
                        "generation": 3.0,
                        "review": 2.0,
                        "conversion": 1.5,
                        "storage": 1.5,
                    },
                    "refinement_instructions": ["Add more details"],
                    "concept": "Test",
                    "components_count": 2,
                    "relationships_count": 1,
                },
            )

        from app.api.diagram import orchestrator

        monkeypatch.setattr(orchestrator, "orchestrate", mock_orchestrate)

        response = client.post(
            "/api/diagram",
            json={"concept": "Test", "educational_level": "14-15"},
        )

        assert response.status_code == 200
        data = response.json()

        # Verify all required fields exist
        required_fields = [
            "png_filename",
            "svg_filename",
            "xml_content",
            "plan",
            "review_score",
            "iterations",
            "total_time_seconds",
            "metadata",
        ]
        for field in required_fields:
            assert field in data

        # Verify plan structure
        assert "diagram_type" in data["plan"]
        assert "components" in data["plan"]
        assert "relationships" in data["plan"]
        assert "success_criteria" in data["plan"]
        assert "educational_level" in data["plan"]
        assert "key_insights" in data["plan"]

        # Verify metadata structure
        assert "step_times" in data["metadata"]
        assert "refinement_instructions" in data["metadata"]
        assert "concept" in data["metadata"]
        assert "components_count" in data["metadata"]
        assert "relationships_count" in data["metadata"]

        # Verify step_times structure
        step_times = data["metadata"]["step_times"]
        required_steps = ["planning", "generation", "review", "conversion", "storage"]
        for step in required_steps:
            assert step in step_times


class TestDiagramEndpointErrors:
    """Test error handling."""

    def test_orchestration_error(self, client, monkeypatch):
        """Test orchestration failure is converted to 500 error."""

        async def mock_orchestrate(*args, **kwargs):
            raise OrchestrationError("Pipeline failed")

        from app.api.diagram import orchestrator

        monkeypatch.setattr(orchestrator, "orchestrate", mock_orchestrate)

        response = client.post(
            "/api/diagram",
            json={"concept": "Test", "educational_level": "11-13"},
        )

        assert response.status_code == 500
        data = response.json()
        # FastAPI wraps detail in a "detail" key
        error_detail = data.get("detail", data)
        assert error_detail["error"] == "orchestration_failed"

    def test_unexpected_error(self, client, monkeypatch):
        """Test unexpected errors are caught and returned as 500."""

        async def mock_orchestrate(*args, **kwargs):
            raise RuntimeError("Unexpected error")

        from app.api.diagram import orchestrator

        monkeypatch.setattr(orchestrator, "orchestrate", mock_orchestrate)

        response = client.post(
            "/api/diagram",
            json={"concept": "Test", "educational_level": "11-13"},
        )

        assert response.status_code == 500
        data = response.json()
        # FastAPI wraps detail in a "detail" key
        error_detail = data.get("detail", data)
        assert error_detail["error"] == "unexpected_error"


class TestDiagramEndpointIntegration:
    """Integration tests for diagram endpoint."""

    def test_health_check_still_works(self, client):
        """Test that existing health check endpoint still works."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    def test_root_endpoint_still_works(self, client):
        """Test that existing root endpoint still works."""
        response = client.get("/")
        assert response.status_code == 200
        assert "VisuaLearn" in response.json()["name"]

    def test_api_documentation_available(self, client):
        """Test that API documentation is available."""
        response = client.get("/docs")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_multiple_concurrent_requests(self, client, monkeypatch):
        """Test that multiple requests can be handled."""

        call_count = [0]

        async def mock_orchestrate(concept, educational_level):
            call_count[0] += 1
            plan = PlanningOutput(
                concept=concept,
                diagram_type="flowchart",
                components=["A"],
                relationships=[],
                success_criteria=["Test"],
                educational_level=educational_level,
                key_insights=["Test"],
            )
            return OrchestrationResult(
                png_filename=f"test_{call_count[0]}.png",
                svg_filename=f"test_{call_count[0]}.svg",
                xml_content="<mxfile></mxfile>",
                plan=plan,
                review_score=90,
                iterations=1,
                total_time_seconds=5.0,
                metadata={
                    "step_times": {
                        "planning": 1.0,
                        "generation": 1.0,
                        "review": 1.0,
                        "conversion": 1.0,
                        "storage": 1.0,
                    },
                    "refinement_instructions": [],
                    "concept": concept,
                    "components_count": 1,
                    "relationships_count": 0,
                },
            )

        from app.api.diagram import orchestrator

        monkeypatch.setattr(orchestrator, "orchestrate", mock_orchestrate)

        # Make multiple requests
        for i in range(3):
            response = client.post(
                "/api/diagram",
                json={"concept": f"Concept {i}", "educational_level": "11-13"},
            )
            assert response.status_code == 200
            assert response.json()["png_filename"] == f"test_{i+1}.png"

        assert call_count[0] == 3
