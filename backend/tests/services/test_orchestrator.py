"""Tests for Orchestrator service."""


import pytest

from app.errors import (
    FileOperationError,
    GenerationError,
    OrchestrationError,
    PlanningError,
    ReviewError,
)
from app.services.orchestrator import Orchestrator, OrchestrationResult
from app.services.planning_agent import PlanningOutput
from app.services.review_agent import ReviewOutput


class TestOrchestratorInit:
    """Test Orchestrator initialization."""

    def test_init_creates_orchestrator(self, test_env):
        """Test successful initialization creates orchestrator."""
        orchestrator = Orchestrator()
        assert orchestrator.planning_agent is not None
        assert orchestrator.diagram_generator is not None
        assert orchestrator.review_agent is not None
        assert orchestrator.image_converter is not None
        assert orchestrator.file_manager is not None


class TestOrchestrationResult:
    """Test OrchestrationResult structure."""

    def test_create_orchestration_result(self, test_env):
        """Test creating orchestration result."""
        plan = PlanningOutput(
            concept="Test",
            diagram_type="flowchart",
            components=["A", "B"],
            relationships=[{"from": "A", "to": "B"}],
            success_criteria=["Test"],
            educational_level="11-13",
            key_insights=["Test insight"],
        )

        result = OrchestrationResult(
            png_filename="test.png",
            svg_filename="test.svg",
            xml_content="<mxfile></mxfile>",
            plan=plan,
            review_score=95,
            iterations=1,
            total_time_seconds=5.5,
            metadata={"test": "value"},
        )

        assert result.png_filename == "test.png"
        assert result.svg_filename == "test.svg"
        assert result.review_score == 95
        assert result.iterations == 1

    def test_orchestration_result_to_dict(self, test_env):
        """Test converting orchestration result to dictionary."""
        plan = PlanningOutput(
            concept="Test",
            diagram_type="flowchart",
            components=["A"],
            relationships=[],
            success_criteria=["Test"],
            educational_level="11-13",
            key_insights=["Test"],
        )

        result = OrchestrationResult(
            png_filename="test.png",
            svg_filename="test.svg",
            xml_content="<mxfile></mxfile>",
            plan=plan,
            review_score=85,
            iterations=2,
            total_time_seconds=10.0,
            metadata={"steps": {}},
        )

        result_dict = result.to_dict()

        assert result_dict["png_filename"] == "test.png"
        assert result_dict["svg_filename"] == "test.svg"
        assert result_dict["review_score"] == 85
        assert result_dict["iterations"] == 2
        assert "plan" in result_dict
        assert isinstance(result_dict["plan"], dict)


class TestOrchestratorPlanningFailure:
    """Test orchestrator handling of planning failures."""

    @pytest.mark.asyncio
    async def test_orchestrate_planning_error(self, test_env, monkeypatch):
        """Test orchestrate raises error when planning fails."""

        async def mock_plan(*args, **kwargs):
            raise PlanningError("Planning failed")

        orchestrator = Orchestrator()
        orchestrator.planning_agent.analyze = mock_plan

        with pytest.raises(OrchestrationError, match="Concept analysis failed"):
            await orchestrator.orchestrate("Test", "11-13")


class TestOrchestratorGenerationFailure:
    """Test orchestrator handling of generation failures."""

    @pytest.mark.asyncio
    async def test_orchestrate_generation_error(self, test_env, monkeypatch):
        """Test orchestrate raises error when generation fails."""

        plan = PlanningOutput(
            concept="Test",
            diagram_type="flowchart",
            components=["A"],
            relationships=[],
            success_criteria=["Test"],
            educational_level="11-13",
            key_insights=["Test"],
        )

        async def mock_plan(*args, **kwargs):
            return plan

        async def mock_generate(*args, **kwargs):
            raise GenerationError("Generation failed")

        orchestrator = Orchestrator()
        orchestrator.planning_agent.analyze = mock_plan
        orchestrator.diagram_generator.generate = mock_generate

        with pytest.raises(OrchestrationError, match="Diagram generation failed"):
            await orchestrator.orchestrate("Test", "11-13")


class TestOrchestratorReviewFailure:
    """Test orchestrator handling of review failures."""

    @pytest.mark.asyncio
    async def test_orchestrate_review_error(self, test_env, monkeypatch):
        """Test orchestrate raises error when review fails."""

        plan = PlanningOutput(
            concept="Test",
            diagram_type="flowchart",
            components=["A"],
            relationships=[],
            success_criteria=["Test"],
            educational_level="11-13",
            key_insights=["Test"],
        )

        async def mock_plan(*args, **kwargs):
            return plan

        async def mock_generate(*args, **kwargs):
            return "<mxfile></mxfile>"

        async def mock_validate(*args, **kwargs):
            raise ReviewError("Review failed")

        orchestrator = Orchestrator()
        orchestrator.planning_agent.analyze = mock_plan
        orchestrator.diagram_generator.generate = mock_generate
        orchestrator.review_agent.validate = mock_validate

        with pytest.raises(OrchestrationError, match="Quality review failed"):
            await orchestrator.orchestrate("Test", "11-13")


class TestOrchestratorConversionFailure:
    """Test orchestrator handling of image conversion failures."""

    @pytest.mark.asyncio
    async def test_orchestrate_conversion_error(self, test_env, monkeypatch):
        """Test orchestrate raises error when image conversion fails."""

        plan = PlanningOutput(
            concept="Test",
            diagram_type="flowchart",
            components=["A"],
            relationships=[],
            success_criteria=["Test"],
            educational_level="11-13",
            key_insights=["Test"],
        )

        review_result = ReviewOutput(
            score=95,
            approved=True,
            feedback="Good",
            refinement_instructions=[],
            iteration=1,
        )

        async def mock_plan(*args, **kwargs):
            return plan

        async def mock_generate(*args, **kwargs):
            return "<mxfile></mxfile>"

        async def mock_validate(*args, **kwargs):
            return review_result

        async def mock_to_png(*args, **kwargs):
            raise Exception("PNG conversion failed")

        orchestrator = Orchestrator()
        orchestrator.planning_agent.analyze = mock_plan
        orchestrator.diagram_generator.generate = mock_generate
        orchestrator.review_agent.validate = mock_validate
        orchestrator.image_converter.to_png = mock_to_png

        with pytest.raises(OrchestrationError, match="Pipeline failed"):
            await orchestrator.orchestrate("Test", "11-13")


class TestOrchestratorStorageFailure:
    """Test orchestrator handling of file storage failures."""

    @pytest.mark.asyncio
    async def test_orchestrate_storage_error_with_cleanup(self, test_env, monkeypatch):
        """Test orchestrate cleans up files when storage fails."""

        plan = PlanningOutput(
            concept="Test",
            diagram_type="flowchart",
            components=["A"],
            relationships=[],
            success_criteria=["Test"],
            educational_level="11-13",
            key_insights=["Test"],
        )

        review_result = ReviewOutput(
            score=95,
            approved=True,
            feedback="Good",
            refinement_instructions=[],
            iteration=1,
        )

        async def mock_plan(*args, **kwargs):
            return plan

        async def mock_generate(*args, **kwargs):
            return "<mxfile></mxfile>"

        async def mock_validate(*args, **kwargs):
            return review_result

        async def mock_to_png(*args, **kwargs):
            return b"PNG_DATA"

        async def mock_to_svg(*args, **kwargs):
            return "<svg></svg>"

        # Track delete calls
        deleted_files = []

        async def mock_save_file(*args, **kwargs):
            raise FileOperationError("Storage failed")

        async def mock_delete_file(filename, *args, **kwargs):
            deleted_files.append(filename)

        orchestrator = Orchestrator()
        orchestrator.planning_agent.analyze = mock_plan
        orchestrator.diagram_generator.generate = mock_generate
        orchestrator.review_agent.validate = mock_validate
        orchestrator.image_converter.to_png = mock_to_png
        orchestrator.image_converter.to_svg = mock_to_svg
        orchestrator.file_manager.save_file = mock_save_file
        orchestrator.file_manager.delete_file = mock_delete_file

        with pytest.raises(OrchestrationError):
            await orchestrator.orchestrate("Test", "11-13")


class TestOrchestratorSuccessful:
    """Test successful orchestration flow."""

    @pytest.mark.asyncio
    async def test_orchestrate_successful_first_approval(self, test_env, monkeypatch):
        """Test successful orchestration with approval on first review."""

        plan = PlanningOutput(
            concept="Photosynthesis",
            diagram_type="flowchart",
            components=["Sunlight", "Water", "CO2", "Glucose"],
            relationships=[
                {"from": "Sunlight", "to": "Energy"},
                {"from": "Water", "to": "Glucose"},
            ],
            success_criteria=["All inputs present", "Clear output"],
            educational_level="11-13",
            key_insights=["Plants make food", "Sunlight is energy source"],
        )

        review_result = ReviewOutput(
            score=95,
            approved=True,
            feedback="Excellent diagram",
            refinement_instructions=[],
            iteration=1,
        )

        async def mock_plan(*args, **kwargs):
            return plan

        async def mock_generate(*args, **kwargs):
            return "<mxfile><diagram>Test</diagram></mxfile>"

        async def mock_validate(*args, **kwargs):
            return review_result

        async def mock_to_png(*args, **kwargs):
            return b"PNG_DATA_BYTES"

        async def mock_to_svg(*args, **kwargs):
            return "<svg></svg>"

        async def mock_save_file(content, file_format):
            if file_format == "png":
                return "test_diagram.png"
            else:
                return "test_diagram.svg"

        orchestrator = Orchestrator()
        orchestrator.planning_agent.analyze = mock_plan
        orchestrator.diagram_generator.generate = mock_generate
        orchestrator.review_agent.validate = mock_validate
        orchestrator.image_converter.to_png = mock_to_png
        orchestrator.image_converter.to_svg = mock_to_svg
        orchestrator.file_manager.save_file = mock_save_file

        result = await orchestrator.orchestrate("Photosynthesis", "11-13")

        assert result.png_filename == "test_diagram.png"
        assert result.svg_filename == "test_diagram.svg"
        assert result.review_score == 95
        assert result.iterations == 1
        assert result.plan.concept == "Photosynthesis"
        assert "<mxfile>" in result.xml_content

    @pytest.mark.asyncio
    async def test_orchestrate_with_multiple_iterations(self, test_env, monkeypatch):
        """Test orchestration with review iterations."""

        plan = PlanningOutput(
            concept="Test",
            diagram_type="flowchart",
            components=["A", "B"],
            relationships=[],
            success_criteria=["Test"],
            educational_level="11-13",
            key_insights=["Test"],
        )

        # First review: not approved
        review_result1 = ReviewOutput(
            score=60,
            approved=False,
            feedback="Needs improvement",
            refinement_instructions=["Add more details"],
            iteration=1,
        )

        # Second review: still not approved
        review_result2 = ReviewOutput(
            score=75,
            approved=False,
            feedback="Better, but incomplete",
            refinement_instructions=["Add labels"],
            iteration=2,
        )

        # Third review: approved
        review_result3 = ReviewOutput(
            score=88,
            approved=True,
            feedback="Good",
            refinement_instructions=[],
            iteration=3,
        )

        call_count = [0]

        async def mock_plan(*args, **kwargs):
            return plan

        async def mock_generate(*args, **kwargs):
            return "<mxfile></mxfile>"

        async def mock_validate(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                return review_result1
            elif call_count[0] == 2:
                return review_result2
            else:
                return review_result3

        async def mock_to_png(*args, **kwargs):
            return b"PNG"

        async def mock_to_svg(*args, **kwargs):
            return "<svg></svg>"

        async def mock_save_file(content, file_format):
            return f"file.{file_format}"

        orchestrator = Orchestrator()
        orchestrator.planning_agent.analyze = mock_plan
        orchestrator.diagram_generator.generate = mock_generate
        orchestrator.review_agent.validate = mock_validate
        orchestrator.image_converter.to_png = mock_to_png
        orchestrator.image_converter.to_svg = mock_to_svg
        orchestrator.file_manager.save_file = mock_save_file

        result = await orchestrator.orchestrate("Test", "11-13")

        assert result.iterations == 3
        assert result.review_score == 88
        assert result.metadata["refinement_instructions"] == [
            "Add more details",
            "Add labels",
        ]


class TestOrchestratorMetadata:
    """Test orchestrator metadata collection."""

    @pytest.mark.asyncio
    async def test_orchestrate_collects_step_times(self, test_env):
        """Test orchestrator collects timing for each step."""

        plan = PlanningOutput(
            concept="Test",
            diagram_type="flowchart",
            components=["A"],
            relationships=[],
            success_criteria=["Test"],
            educational_level="11-13",
            key_insights=["Test"],
        )

        review_result = ReviewOutput(
            score=90,
            approved=True,
            feedback="Good",
            refinement_instructions=[],
            iteration=1,
        )

        async def mock_plan(*args, **kwargs):
            return plan

        async def mock_generate(*args, **kwargs):
            return "<mxfile></mxfile>"

        async def mock_validate(*args, **kwargs):
            return review_result

        async def mock_to_png(*args, **kwargs):
            return b"PNG"

        async def mock_to_svg(*args, **kwargs):
            return "<svg></svg>"

        async def mock_save_file(content, file_format):
            return f"file.{file_format}"

        orchestrator = Orchestrator()
        orchestrator.planning_agent.analyze = mock_plan
        orchestrator.diagram_generator.generate = mock_generate
        orchestrator.review_agent.validate = mock_validate
        orchestrator.image_converter.to_png = mock_to_png
        orchestrator.image_converter.to_svg = mock_to_svg
        orchestrator.file_manager.save_file = mock_save_file

        result = await orchestrator.orchestrate("Test", "11-13")

        assert "step_times" in result.metadata
        assert "planning" in result.metadata["step_times"]
        assert "generation" in result.metadata["step_times"]
        assert "review" in result.metadata["step_times"]
        assert "conversion" in result.metadata["step_times"]
        assert "storage" in result.metadata["step_times"]
        assert result.total_time_seconds > 0

    @pytest.mark.asyncio
    async def test_orchestrate_collects_plan_metadata(self, test_env):
        """Test orchestrator collects planning metadata."""

        plan = PlanningOutput(
            concept="Complex Concept",
            diagram_type="mindmap",
            components=["A", "B", "C", "D"],
            relationships=[
                {"from": "A", "to": "B"},
                {"from": "B", "to": "C"},
            ],
            success_criteria=["Test"],
            educational_level="14-15",
            key_insights=["Insight1", "Insight2"],
        )

        review_result = ReviewOutput(
            score=92,
            approved=True,
            feedback="Great",
            refinement_instructions=[],
            iteration=1,
        )

        async def mock_plan(*args, **kwargs):
            return plan

        async def mock_generate(*args, **kwargs):
            return "<mxfile></mxfile>"

        async def mock_validate(*args, **kwargs):
            return review_result

        async def mock_to_png(*args, **kwargs):
            return b"PNG"

        async def mock_to_svg(*args, **kwargs):
            return "<svg></svg>"

        async def mock_save_file(content, file_format):
            return f"file.{file_format}"

        orchestrator = Orchestrator()
        orchestrator.planning_agent.analyze = mock_plan
        orchestrator.diagram_generator.generate = mock_generate
        orchestrator.review_agent.validate = mock_validate
        orchestrator.image_converter.to_png = mock_to_png
        orchestrator.image_converter.to_svg = mock_to_svg
        orchestrator.file_manager.save_file = mock_save_file

        result = await orchestrator.orchestrate("Complex Concept", "14-15")

        assert result.metadata["concept"] == "Complex Concept"
        assert result.metadata["components_count"] == 4
        assert result.metadata["relationships_count"] == 2


class TestOrchestratorIntegration:
    """Integration tests for Orchestrator."""

    @pytest.mark.asyncio
    async def test_orchestration_full_pipeline_integration(self, test_env):
        """Test complete orchestration pipeline with all real service interfaces."""

        plan = PlanningOutput(
            concept="Water Cycle",
            diagram_type="flowchart",
            components=["Evaporation", "Condensation", "Precipitation", "Collection"],
            relationships=[
                {"from": "Evaporation", "to": "Condensation"},
                {"from": "Condensation", "to": "Precipitation"},
                {"from": "Precipitation", "to": "Collection"},
            ],
            success_criteria=["All stages present"],
            educational_level="8-10",
            key_insights=["Continuous cycle"],
        )

        review_result = ReviewOutput(
            score=94,
            approved=True,
            feedback="Educational",
            refinement_instructions=[],
            iteration=1,
        )

        async def mock_plan(*args, **kwargs):
            return plan

        async def mock_generate(*args, **kwargs):
            return "<mxfile><diagram>Water Cycle</diagram></mxfile>"

        async def mock_validate(*args, **kwargs):
            return review_result

        async def mock_to_png(*args, **kwargs):
            return b"\x89PNG\r\n\x1a\n" + b"mock_png_data"

        async def mock_to_svg(*args, **kwargs):
            return "<svg><text>Water Cycle</text></svg>"

        async def mock_save_file(content, file_format):
            return f"water_cycle_{len(content)}.{file_format}"

        orchestrator = Orchestrator()
        orchestrator.planning_agent.analyze = mock_plan
        orchestrator.diagram_generator.generate = mock_generate
        orchestrator.review_agent.validate = mock_validate
        orchestrator.image_converter.to_png = mock_to_png
        orchestrator.image_converter.to_svg = mock_to_svg
        orchestrator.file_manager.save_file = mock_save_file

        result = await orchestrator.orchestrate("Water Cycle", "8-10")

        # Verify complete result structure
        assert isinstance(result, OrchestrationResult)
        assert result.plan.concept == "Water Cycle"
        assert result.plan.diagram_type == "flowchart"
        assert len(result.plan.components) == 4
        assert result.review_score == 94
        assert result.iterations == 1
        assert result.xml_content == "<mxfile><diagram>Water Cycle</diagram></mxfile>"
        assert ".png" in result.png_filename
        assert ".svg" in result.svg_filename
        assert result.total_time_seconds > 0
        assert result.metadata["concept"] == "Water Cycle"
