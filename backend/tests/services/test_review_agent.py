"""Tests for Review Agent service."""

import asyncio
import json
from unittest.mock import MagicMock

import pytest

from app.errors import ReviewError
from app.services.planning_agent import PlanningOutput
from app.services.review_agent import ReviewAgent, ReviewOutput


class TestReviewOutput:
    """Test ReviewOutput class."""

    def test_init_valid_data(self):
        """Test ReviewOutput initialization with valid data."""
        output = ReviewOutput(
            score=85,
            approved=False,
            feedback="Good diagram but needs refinement",
            refinement_instructions=["Add labels to nodes", "Clarify relationships"],
            iteration=1,
        )

        assert output.score == 85
        assert output.approved is False
        assert output.feedback == "Good diagram but needs refinement"
        assert len(output.refinement_instructions) == 2
        assert output.iteration == 1

    def test_to_dict_conversion(self):
        """Test conversion to dictionary."""
        output = ReviewOutput(
            score=92,
            approved=True,
            feedback="Excellent diagram",
            refinement_instructions=[],
            iteration=1,
        )

        result = output.to_dict()
        assert isinstance(result, dict)
        assert result["score"] == 92
        assert result["approved"] is True
        assert result["feedback"] == "Excellent diagram"
        assert result["refinement_instructions"] == []


class TestReviewAgentInit:
    """Test ReviewAgent initialization."""

    def test_init_creates_agent(self, test_env, mock_google_generativeai):
        """Test successful initialization creates agent."""
        mock_google_generativeai.GenerativeModel.return_value = MagicMock()
        agent = ReviewAgent()
        assert agent.timeout == 3
        assert agent.max_iterations == 3


class TestReviewAgentValidate:
    """Test ReviewAgent.validate() method."""

    @pytest.mark.asyncio
    async def test_validate_empty_xml(self, test_env, mock_google_generativeai):
        """Test validate raises error with empty XML."""
        agent = ReviewAgent()
        plan = PlanningOutput(
            concept="Test",
            diagram_type="flowchart",
            components=["A", "B"],
            relationships=[],
            success_criteria=["Test"],
            educational_level="11-13",
            key_insights=["Test"],
        )

        with pytest.raises(ReviewError, match="XML cannot be empty"):
            await agent.validate("", plan)

    @pytest.mark.asyncio
    async def test_validate_whitespace_xml(self, test_env, mock_google_generativeai):
        """Test validate raises error with whitespace-only XML."""
        agent = ReviewAgent()
        plan = PlanningOutput(
            concept="Test",
            diagram_type="flowchart",
            components=["A", "B"],
            relationships=[],
            success_criteria=["Test"],
            educational_level="11-13",
            key_insights=["Test"],
        )

        with pytest.raises(ReviewError, match="XML cannot be empty"):
            await agent.validate("   ", plan)

    @pytest.mark.asyncio
    async def test_validate_invalid_iteration(self, test_env, mock_google_generativeai):
        """Test validate raises error with invalid iteration."""
        agent = ReviewAgent()
        plan = PlanningOutput(
            concept="Test",
            diagram_type="flowchart",
            components=["A", "B"],
            relationships=[],
            success_criteria=["Test"],
            educational_level="11-13",
            key_insights=["Test"],
        )
        xml = "<mxfile></mxfile>"

        with pytest.raises(ReviewError, match="Invalid iteration"):
            await agent.validate(xml, plan, iteration=0)

        with pytest.raises(ReviewError, match="Invalid iteration"):
            await agent.validate(xml, plan, iteration=4)

    @pytest.mark.asyncio
    async def test_validate_timeout(self, test_env, mock_google_generativeai):
        """Test validate raises timeout error."""

        # Create a mock that never completes
        async def slow_review(*args, **kwargs):
            await asyncio.sleep(10)

        mock_client = MagicMock()
        mock_client.generate_content = slow_review
        mock_google_generativeai.GenerativeModel.return_value = mock_client

        agent = ReviewAgent()
        agent.timeout = 0.001  # Set very short timeout

        plan = PlanningOutput(
            concept="Test",
            diagram_type="flowchart",
            components=["A"],
            relationships=[],
            success_criteria=["Test"],
            educational_level="11-13",
            key_insights=["Test"],
        )

        with pytest.raises(ReviewError):
            await agent.validate("<mxfile></mxfile>", plan)

    @pytest.mark.asyncio
    async def test_validate_invalid_json_response(
        self, test_env, mock_google_generativeai
    ):
        """Test validate raises error with invalid JSON."""
        response_mock = MagicMock()
        response_mock.text = "Not valid JSON at all"

        mock_client = MagicMock()
        mock_client.generate_content = MagicMock(return_value=response_mock)
        mock_google_generativeai.GenerativeModel.return_value = mock_client

        agent = ReviewAgent()
        plan = PlanningOutput(
            concept="Test",
            diagram_type="flowchart",
            components=["A"],
            relationships=[],
            success_criteria=["Test"],
            educational_level="11-13",
            key_insights=["Test"],
        )

        with pytest.raises(ReviewError):
            await agent.validate("<mxfile></mxfile>", plan)

    @pytest.mark.asyncio
    async def test_validate_missing_required_field(
        self, test_env, mock_google_generativeai
    ):
        """Test validate raises error when required field is missing."""
        invalid_response = {
            "score": 85,
            # Missing feedback
            "refinement_instructions": ["Fix labels"],
        }

        response_mock = MagicMock()
        response_mock.text = json.dumps(invalid_response)

        mock_client = MagicMock()
        mock_client.generate_content = MagicMock(return_value=response_mock)
        mock_google_generativeai.GenerativeModel.return_value = mock_client

        agent = ReviewAgent()
        plan = PlanningOutput(
            concept="Test",
            diagram_type="flowchart",
            components=["A"],
            relationships=[],
            success_criteria=["Test"],
            educational_level="11-13",
            key_insights=["Test"],
        )

        with pytest.raises(ReviewError):
            await agent.validate("<mxfile></mxfile>", plan)

    @pytest.mark.asyncio
    async def test_validate_invalid_score(self, test_env, mock_google_generativeai):
        """Test validate raises error with invalid score."""
        invalid_response = {
            "score": 150,  # Invalid - should be 0-100
            "feedback": "Test",
            "refinement_instructions": [],
        }

        response_mock = MagicMock()
        response_mock.text = json.dumps(invalid_response)

        mock_client = MagicMock()
        mock_client.generate_content = MagicMock(return_value=response_mock)
        mock_google_generativeai.GenerativeModel.return_value = mock_client

        agent = ReviewAgent()
        plan = PlanningOutput(
            concept="Test",
            diagram_type="flowchart",
            components=["A"],
            relationships=[],
            success_criteria=["Test"],
            educational_level="11-13",
            key_insights=["Test"],
        )

        with pytest.raises(ReviewError):
            await agent.validate("<mxfile></mxfile>", plan)


class TestReviewAgentApprovalLogic:
    """Test approval decision logic."""

    def test_approve_high_score(self, test_env, mock_google_generativeai):
        """Test approval with score >= 90."""
        agent = ReviewAgent()

        # Score 95 should always be approved
        assert agent._determine_approval(95, 1) is True
        assert agent._determine_approval(95, 2) is True
        assert agent._determine_approval(90, 3) is True

    def test_refinement_medium_score(self, test_env, mock_google_generativeai):
        """Test refinement request with score 70-89."""
        agent = ReviewAgent()

        # Score 70-89 should request refinement (not approved)
        assert agent._determine_approval(70, 1) is False
        assert agent._determine_approval(75, 2) is False
        assert agent._determine_approval(89, 3) is False

    def test_accept_low_score_final_iteration(self, test_env, mock_google_generativeai):
        """Test accepting low score on final iteration."""
        agent = ReviewAgent()

        # Score <70 should be rejected except on final iteration
        assert agent._determine_approval(69, 1) is False
        assert agent._determine_approval(60, 2) is False
        assert (
            agent._determine_approval(50, 3) is True
        )  # Final iteration - accept anyway

    def test_boundary_scores(self, test_env, mock_google_generativeai):
        """Test boundary values for score ranges."""
        agent = ReviewAgent()

        # Test boundaries
        assert agent._determine_approval(90, 1) is True  # Boundary: approve
        assert agent._determine_approval(89, 1) is False  # Boundary: refinement
        assert agent._determine_approval(70, 1) is False  # Boundary: refinement
        assert agent._determine_approval(69, 1) is False  # Boundary: reject
        assert (
            agent._determine_approval(69, 3) is True
        )  # Boundary: final iteration accept


class TestReviewAgentParseJson:
    """Test JSON parsing functionality."""

    def test_parse_json_bare_json(self, test_env, mock_google_generativeai):
        """Test parsing bare JSON without markdown."""
        agent = ReviewAgent()

        json_text = '{"score": 85, "feedback": "Good"}'
        result = agent._parse_json_response(json_text)

        assert result["score"] == 85
        assert result["feedback"] == "Good"

    def test_parse_json_with_markdown_code_block(
        self, test_env, mock_google_generativeai
    ):
        """Test parsing JSON with ```json code block."""
        agent = ReviewAgent()

        json_text = """```json
{"score": 92, "feedback": "Excellent", "refinement_instructions": []}
```"""
        result = agent._parse_json_response(json_text)

        assert result["score"] == 92
        assert result["feedback"] == "Excellent"

    def test_parse_json_with_generic_code_block(
        self, test_env, mock_google_generativeai
    ):
        """Test parsing JSON with generic ``` code block."""
        agent = ReviewAgent()

        json_text = """```
{"score": 75, "feedback": "Good", "refinement_instructions": ["Fix labels"]}
```"""
        result = agent._parse_json_response(json_text)

        assert result["score"] == 75

    def test_parse_json_with_whitespace(self, test_env, mock_google_generativeai):
        """Test parsing JSON with extra whitespace."""
        agent = ReviewAgent()

        json_text = """

```json
{"score": 80, "feedback": "OK"}
```

  """
        result = agent._parse_json_response(json_text)

        assert result["score"] == 80

    def test_parse_json_invalid_json(self, test_env, mock_google_generativeai):
        """Test parsing invalid JSON raises error."""
        agent = ReviewAgent()

        with pytest.raises(json.JSONDecodeError):
            agent._parse_json_response("not json")

    def test_parse_json_complex_structure(self, test_env, mock_google_generativeai):
        """Test parsing complex JSON structure."""
        agent = ReviewAgent()

        json_text = """```json
{
  "score": 87,
  "feedback": "Good diagram with minor issues",
  "refinement_instructions": [
    "Add more labels",
    "Clarify relationships",
    "Improve spacing"
  ],
  "approved": false
}
```"""
        result = agent._parse_json_response(json_text)

        assert result["score"] == 87
        assert len(result["refinement_instructions"]) == 3
        assert result["approved"] is False


class TestReviewAgentIntegration:
    """Integration tests for Review Agent."""

    @pytest.mark.asyncio
    async def test_error_handling_cascade(self, test_env, mock_google_generativeai):
        """Test error is properly caught and re-raised as ReviewError."""
        mock_client = MagicMock()
        # Simulate API error
        mock_client.generate_content = MagicMock(
            side_effect=RuntimeError("API Connection failed")
        )
        mock_google_generativeai.GenerativeModel.return_value = mock_client

        agent = ReviewAgent()
        plan = PlanningOutput(
            concept="Test",
            diagram_type="flowchart",
            components=["A"],
            relationships=[],
            success_criteria=["Test"],
            educational_level="11-13",
            key_insights=["Test"],
        )

        with pytest.raises(ReviewError, match="Failed to review diagram"):
            await agent.validate("<mxfile></mxfile>", plan)

    @pytest.mark.asyncio
    async def test_validate_iteration_parameter_validation(
        self, test_env, mock_google_generativeai
    ):
        """Test that iteration parameter is validated correctly."""
        agent = ReviewAgent()
        plan = PlanningOutput(
            concept="Test",
            diagram_type="flowchart",
            components=["A"],
            relationships=[],
            success_criteria=["Test"],
            educational_level="11-13",
            key_insights=["Test"],
        )

        # Test that invalid iterations are rejected
        with pytest.raises(ReviewError, match="Invalid iteration 0"):
            await agent.validate("<mxfile></mxfile>", plan, 0)

        with pytest.raises(ReviewError, match="Invalid iteration 4"):
            await agent.validate("<mxfile></mxfile>", plan, 4)
