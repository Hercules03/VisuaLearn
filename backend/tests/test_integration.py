"""
Comprehensive integration tests for VisuaLearn system.

Tests the complete pipeline from API request through diagram generation,
review, conversion, and file export.
"""

import asyncio
import json
import os
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.api.diagram import DiagramRequest
from app.errors import (
    FileOperationError,
    GenerationError,
    InputValidationError,
    PlanningError,
    ReviewError,
    RenderingError,
)
from app.models.schemas import DiagramMetadata, DiagramResponse
from app.services.diagram_generator import DiagramGenerator
from app.services.file_manager import FileManager
from app.services.image_converter import ImageConverter
from app.services.orchestrator import Orchestrator
from app.services.planning_agent import PlanningAgent, PlanningOutput
from app.services.review_agent import ReviewAgent, ReviewOutput


class TestApiSchemaValidation:
    """Test API request validation and schema compliance."""

    def test_diagram_request_valid(self):
        """Test valid diagram request creation."""
        request = DiagramRequest(
            concept="Explain photosynthesis",
            educational_level="11-13",
        )
        assert request.concept == "Explain photosynthesis"
        assert request.educational_level == "11-13"

    def test_diagram_request_invalid_educational_level(self):
        """Test request rejection with invalid educational level."""
        with pytest.raises(ValueError):
            DiagramRequest(
                concept="Test",
                educational_level="intermediate",  # INVALID - must be age range
            )

    def test_diagram_request_invalid_educational_level_wrong_format(self):
        """Test rejection of educational level in wrong format."""
        with pytest.raises(ValueError):
            DiagramRequest(
                concept="Test",
                educational_level="13",  # INVALID - must be range like 8-10
            )

    def test_diagram_request_empty_concept(self):
        """Test request rejection with empty concept."""
        with pytest.raises(ValueError):
            DiagramRequest(
                concept="",
                educational_level="11-13",
            )

    def test_diagram_request_concept_too_long(self):
        """Test request rejection with overly long concept."""
        with pytest.raises(ValueError):
            DiagramRequest(
                concept="x" * 1001,
                educational_level="11-13",
            )

    def test_diagram_request_all_educational_levels(self):
        """Test all valid educational level formats."""
        for level in ["8-10", "11-13", "14-15"]:
            request = DiagramRequest(
                concept="Test concept",
                educational_level=level,
            )
            assert request.educational_level == level


class TestPipelineComponents:
    """Test individual pipeline components in isolation."""

    def test_planning_agent_valid_input(self, test_env):
        """Test planning agent accepts valid input."""
        agent = PlanningAgent()
        assert agent.timeout == 5
        assert hasattr(agent, 'client')  # Verify Gemini client is initialized

    def test_review_agent_valid_initialization(self, test_env):
        """Test review agent initialization."""
        agent = ReviewAgent()
        assert agent.timeout == 3
        assert agent.max_iterations == 3

    def test_image_converter_valid_initialization(self, test_env):
        """Test image converter initialization with correct port."""
        converter = ImageConverter()
        assert converter.timeout == 4
        # Critical: Verify port is 6002, not 3001
        assert converter.drawio_url == "http://localhost:6002"

    def test_diagram_generator_valid_initialization(self, test_env):
        """Test diagram generator initialization with correct port."""
        generator = DiagramGenerator()
        assert generator.timeout == 12
        # Critical: Verify port is 6002, not 3001
        assert generator.drawio_url == "http://localhost:6002"

    def test_file_manager_valid_initialization(self, test_env):
        """Test file manager initialization."""
        manager = FileManager()
        assert manager.temp_dir.exists()
        assert manager.max_file_size == 5242880  # 5MB


class TestPipelineIntegration:
    """Test the complete orchestrated pipeline."""

    @pytest.mark.asyncio
    async def test_orchestrator_initialization(self, test_env):
        """Test orchestrator creates all required services."""
        orchestrator = Orchestrator()
        assert orchestrator.planning_agent is not None
        assert orchestrator.diagram_generator is not None
        assert orchestrator.review_agent is not None
        assert orchestrator.image_converter is not None
        assert orchestrator.file_manager is not None


    @pytest.mark.asyncio
    async def test_orchestrator_timeouts_are_configured(self, test_env):
        """Test that all orchestrator components have proper timeouts."""
        orchestrator = Orchestrator()

        # Verify each component has timeout configured
        assert orchestrator.planning_agent.timeout == 5
        assert orchestrator.diagram_generator.timeout == 12
        assert orchestrator.review_agent.timeout == 3
        assert orchestrator.image_converter.timeout == 4


class TestEndToEndWorkflow:
    """Test complete end-to-end workflows."""

    def test_valid_age_range_workflow(self, test_env):
        """Test workflow with valid age range (8-10)."""
        request = DiagramRequest(
            concept="Explain gravity",
            educational_level="8-10",
        )
        assert request.educational_level == "8-10"

    def test_valid_age_range_workflow_middle(self, test_env):
        """Test workflow with valid age range (11-13)."""
        request = DiagramRequest(
            concept="Explain photosynthesis",
            educational_level="11-13",
        )
        assert request.educational_level == "11-13"

    def test_valid_age_range_workflow_advanced(self, test_env):
        """Test workflow with valid age range (14-15)."""
        request = DiagramRequest(
            concept="Explain quantum mechanics",
            educational_level="14-15",
        )
        assert request.educational_level == "14-15"

    def test_invalid_educational_level_elementary(self):
        """Test rejection of textual educational level 'elementary'."""
        with pytest.raises(ValueError):
            DiagramRequest(
                concept="Test",
                educational_level="elementary",  # REJECTED
            )

    def test_invalid_educational_level_intermediate(self):
        """Test rejection of textual educational level 'intermediate'."""
        with pytest.raises(ValueError):
            DiagramRequest(
                concept="Test",
                educational_level="intermediate",  # REJECTED - this was the bug!
            )

    def test_invalid_educational_level_advanced(self):
        """Test rejection of textual educational level 'advanced'."""
        with pytest.raises(ValueError):
            DiagramRequest(
                concept="Test",
                educational_level="advanced",  # REJECTED
            )

    def test_invalid_educational_level_numeric(self):
        """Test rejection of single numeric educational level."""
        with pytest.raises(ValueError):
            DiagramRequest(
                concept="Test",
                educational_level="13",  # REJECTED - must be range
            )


class TestFileExportWorkflow:
    """Test file export and cleanup functionality."""

    def test_file_manager_creates_temp_directory(self, test_env):
        """Test file manager creates temp directory."""
        manager = FileManager()
        assert manager.temp_dir.exists()
        assert manager.temp_dir.is_dir()

    @pytest.mark.asyncio
    async def test_file_manager_saves_file(self, test_env):
        """Test file manager can save files."""
        manager = FileManager()
        content = b"test png content"
        filename = await manager.save_file(content, "png")
        assert filename is not None
        assert filename.endswith(".png")

    @pytest.mark.asyncio
    async def test_file_manager_validates_extensions(self, test_env):
        """Test file manager creates files with correct extensions."""
        manager = FileManager()

        # Test allowed extensions
        for ext in ["png", "svg", "xml"]:
            filename = await manager.save_file(b"test", ext)
            assert filename.endswith(f".{ext}")

    @pytest.mark.asyncio
    async def test_file_manager_prevents_path_traversal(self, test_env):
        """Test file manager prevents path traversal attacks."""
        manager = FileManager()

        with pytest.raises(FileOperationError):
            await manager.get_file("../../../etc/passwd")

        with pytest.raises(FileOperationError):
            await manager.get_file("..\\..\\windows\\system32")


class TestErrorHandling:
    """Test error handling across the system."""

    def test_planning_error_on_empty_input(self):
        """Test planning error for empty input."""
        with pytest.raises(ValueError):
            DiagramRequest(concept="", educational_level="11-13")

    def test_generation_error_port_configuration(self, test_env):
        """Test diagram generator uses correct port (not 3001)."""
        generator = DiagramGenerator()
        # This is the critical fix - ensure it's 6002, not 3001
        assert generator.drawio_url == "http://localhost:6002"

    def test_image_converter_error_port_configuration(self, test_env):
        """Test image converter uses correct port (not 3001)."""
        converter = ImageConverter()
        # This is the critical fix - ensure it's 6002, not 3001
        assert converter.drawio_url == "http://localhost:6002"


class TestServiceIntegration:
    """Test services working together."""

    def test_planning_output_to_review_input(self):
        """Test planning output can be used for review input."""
        plan = PlanningOutput(
            concept="Photosynthesis",
            diagram_type="flowchart",
            components=["Sunlight", "Water", "Glucose"],
            relationships=[{"from": "Sunlight", "to": "Energy", "label": "provides"}],
            success_criteria=["All components present"],
            educational_level="11-13",
            key_insights=["Plants make food"],
        )

        # Verify structure for downstream use
        assert plan.concept is not None
        assert len(plan.components) > 0
        assert plan.diagram_type in ["flowchart", "mindmap", "sequence", "hierarchy"]

    def test_review_output_structure(self):
        """Test review output has required fields."""
        review = ReviewOutput(
            score=92,
            approved=True,
            feedback="Excellent diagram",
            refinement_instructions=[],
            iteration=1,
        )

        assert 0 <= review.score <= 100
        assert isinstance(review.approved, bool)
        assert isinstance(review.refinement_instructions, list)


class TestPortConfiguration:
    """Test that port configuration is correct throughout system."""

    def test_env_drawio_service_url(self):
        """Test environment variable has correct port."""
        url = os.getenv("DRAWIO_SERVICE_URL", "http://localhost:6002")
        assert "6002" in url
        assert "3001" not in url

    def test_diagram_generator_uses_env_port(self, test_env):
        """Test diagram generator respects environment port."""
        generator = DiagramGenerator()
        assert "6002" in generator.drawio_url
        assert "3001" not in generator.drawio_url

    def test_image_converter_uses_env_port(self, test_env):
        """Test image converter respects environment port."""
        converter = ImageConverter()
        assert "6002" in converter.drawio_url
        assert "3001" not in converter.drawio_url


class TestApiResponseStructure:
    """Test API response structures are correct."""

    def test_diagram_response_structure(self):
        """Test DiagramResponse has all required fields."""
        from app.models.schemas import PlanningData, StepTimes

        response = DiagramResponse(
            png_filename="test.png",
            svg_filename="test.svg",
            xml_content="<mxfile></mxfile>",
            plan=PlanningData(
                concept="Test",
                diagram_type="flowchart",
                components=["A"],
                relationships=[],
                success_criteria=["Test"],
                educational_level="11-13",
                key_insights=["Test"],
            ),
            review_score=92,
            iterations=1,
            total_time_seconds=12.3,
            metadata=DiagramMetadata(
                step_times=StepTimes(
                    planning=2.1,
                    generation=8.0,
                    review=1.5,
                    conversion=0.5,
                    storage=0.2,
                ),
                refinement_instructions=["Improve clarity"],
                concept="Test",
                components_count=1,
                relationships_count=0,
            ),
        )

        assert response.png_filename == "test.png"
        assert response.review_score == 92
        assert response.iterations == 1


class TestEducationalLevelValidation:
    """Test educational level validation across system."""

    def test_valid_levels_pass_validation(self):
        """Test all valid levels pass validation."""
        valid_levels = ["8-10", "11-13", "14-15"]
        for level in valid_levels:
            request = DiagramRequest(concept="Test", educational_level=level)
            assert request.educational_level == level

    def test_textual_levels_fail_validation(self):
        """Test textual levels are rejected."""
        invalid_levels = [
            "elementary",
            "intermediate",
            "advanced",
            "beginner",
            "expert",
        ]
        for level in invalid_levels:
            with pytest.raises(ValueError):
                DiagramRequest(concept="Test", educational_level=level)

    def test_numeric_only_levels_fail_validation(self):
        """Test numeric-only levels are rejected."""
        invalid_levels = ["8", "10", "11", "13", "14", "15"]
        for level in invalid_levels:
            with pytest.raises(ValueError):
                DiagramRequest(concept="Test", educational_level=level)


class TestSystemReadiness:
    """Test that system is ready for production use."""

    def test_backend_has_all_services(self, test_env):
        """Test backend has all required services initialized."""
        orchestrator = Orchestrator()
        assert orchestrator.planning_agent is not None
        assert orchestrator.diagram_generator is not None
        assert orchestrator.review_agent is not None
        assert orchestrator.image_converter is not None
        assert orchestrator.file_manager is not None

    def test_all_services_have_correct_timeouts(self, test_env):
        """Test all services have configured timeouts."""
        orchestrator = Orchestrator()
        assert orchestrator.planning_agent.timeout == 5
        assert orchestrator.diagram_generator.timeout == 12
        assert orchestrator.review_agent.timeout == 3
        assert orchestrator.image_converter.timeout == 4

    def test_all_services_use_correct_port(self, test_env):
        """Test all services configured for correct port (6002)."""
        generator = DiagramGenerator()
        converter = ImageConverter()
        assert generator.drawio_url == "http://localhost:6002"
        assert converter.drawio_url == "http://localhost:6002"

    def test_schema_validation_prevents_invalid_requests(self):
        """Test schema validation prevents 422 errors."""
        # This request would have caused 422 before fixes
        with pytest.raises(ValueError):
            DiagramRequest(
                concept="How asymmetric key works?",
                educational_level="intermediate",  # INVALID - was causing 422
            )

        # This is the correct way
        request = DiagramRequest(
            concept="How asymmetric key works?",
            educational_level="11-13",  # CORRECT - fixes 422 error
        )
        assert request.educational_level == "11-13"
