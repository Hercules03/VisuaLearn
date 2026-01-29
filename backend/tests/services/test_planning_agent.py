"""Tests for Planning Agent service."""

import asyncio
import json
from unittest.mock import MagicMock

import pytest

from app.errors import PlanningError
from app.services.planning_agent import PlanningAgent, PlanningOutput


class TestPlanningOutput:
    """Test PlanningOutput class."""

    def test_init_valid_data(self):
        """Test PlanningOutput initialization with valid data."""
        output = PlanningOutput(
            concept="Photosynthesis",
            diagram_type="flowchart",
            components=["Sunlight", "Water"],
            relationships=[{"from": "A", "to": "B", "label": "leads to"}],
            success_criteria=["Clear diagram"],
            educational_level="11-13",
            key_insights=["Plants make food"],
        )

        assert output.concept == "Photosynthesis"
        assert output.diagram_type == "flowchart"
        assert len(output.components) == 2
        assert output.educational_level == "11-13"

    def test_to_dict_conversion(self):
        """Test conversion to dictionary."""
        output = PlanningOutput(
            concept="Test",
            diagram_type="mindmap",
            components=["A", "B"],
            relationships=[],
            success_criteria=["Test"],
            educational_level="8-10",
            key_insights=["Insight"],
        )

        result = output.to_dict()
        assert isinstance(result, dict)
        assert result["concept"] == "Test"
        assert result["diagram_type"] == "mindmap"
        assert result["components"] == ["A", "B"]
        assert result["educational_level"] == "8-10"


class TestPlanningAgentInit:
    """Test PlanningAgent initialization."""

    def test_init_creates_agent(self, test_env, mock_google_generativeai):
        """Test successful initialization creates agent."""
        mock_google_generativeai.GenerativeModel.return_value = MagicMock()
        agent = PlanningAgent()
        assert agent.timeout == 5


class TestPlanningAgentAnalyze:
    """Test PlanningAgent.analyze() method."""

    @pytest.mark.asyncio
    async def test_analyze_empty_input(self, test_env, mock_google_generativeai):
        """Test analyze raises error with empty input."""
        agent = PlanningAgent()

        with pytest.raises(PlanningError, match="Topic cannot be empty"):
            await agent.analyze("")

    @pytest.mark.asyncio
    async def test_analyze_whitespace_input(self, test_env, mock_google_generativeai):
        """Test analyze raises error with whitespace-only input."""
        agent = PlanningAgent()

        with pytest.raises(PlanningError, match="Topic cannot be empty"):
            await agent.analyze("   ")

    @pytest.mark.asyncio
    async def test_analyze_input_too_long(self, test_env, mock_google_generativeai):
        """Test analyze raises error with input exceeding max length."""
        agent = PlanningAgent()
        long_input = "x" * 1001  # Exceeds 1000 char limit

        with pytest.raises(PlanningError, match="Topic is too long"):
            await agent.analyze(long_input)

    @pytest.mark.asyncio
    async def test_analyze_timeout(self, test_env, mock_google_generativeai):
        """Test analyze raises timeout error."""
        # Create a mock that never completes
        async def slow_analysis(*args, **kwargs):
            await asyncio.sleep(10)  # Sleep longer than timeout

        mock_client = MagicMock()
        mock_client.generate_content = slow_analysis
        mock_google_generativeai.GenerativeModel.return_value = mock_client

        agent = PlanningAgent()
        agent.timeout = 0.001  # Set very short timeout

        with pytest.raises(PlanningError):
            await agent.analyze("test topic")

    @pytest.mark.asyncio
    async def test_analyze_invalid_json_response(self, test_env, mock_google_generativeai):
        """Test analyze raises error with invalid JSON from Gemini."""
        response_mock = MagicMock()
        response_mock.text = "Not valid JSON at all"

        mock_client = MagicMock()
        mock_client.generate_content = MagicMock(return_value=response_mock)
        mock_google_generativeai.GenerativeModel.return_value = mock_client

        agent = PlanningAgent()

        with pytest.raises(PlanningError):
            await agent.analyze("test topic")

    @pytest.mark.asyncio
    async def test_analyze_missing_required_field(self, test_env, mock_google_generativeai):
        """Test analyze raises error when required field is missing."""
        invalid_response = {
            "concept": "Test",
            # Missing diagram_type
            "components": ["A"],
            "relationships": [],
            "success_criteria": ["Test"],
            "educational_level": "11-13",
            "key_insights": ["Test"],
        }

        mock_client = MagicMock()
        response_mock = MagicMock()
        response_mock.text = json.dumps(invalid_response)
        mock_client.generate_content = MagicMock(return_value=response_mock)
        mock_google_generativeai.GenerativeModel.return_value = mock_client

        agent = PlanningAgent()

        with pytest.raises(PlanningError):
            await agent.analyze("test topic")

    @pytest.mark.asyncio
    async def test_analyze_invalid_diagram_type(self, test_env, mock_google_generativeai):
        """Test analyze raises error with invalid diagram type."""
        invalid_response = {
            "concept": "Test",
            "diagram_type": "invalid_type",
            "components": ["A"],
            "relationships": [],
            "success_criteria": ["Test"],
            "educational_level": "11-13",
            "key_insights": ["Test"],
        }

        mock_client = MagicMock()
        response_mock = MagicMock()
        response_mock.text = json.dumps(invalid_response)
        mock_client.generate_content = MagicMock(return_value=response_mock)
        mock_google_generativeai.GenerativeModel.return_value = mock_client

        agent = PlanningAgent()

        with pytest.raises(PlanningError):
            await agent.analyze("test topic")

    @pytest.mark.asyncio
    async def test_analyze_invalid_educational_level(self, test_env, mock_google_generativeai):
        """Test analyze raises error with invalid educational level."""
        invalid_response = {
            "concept": "Test",
            "diagram_type": "flowchart",
            "components": ["A"],
            "relationships": [],
            "success_criteria": ["Test"],
            "educational_level": "99-100",  # Invalid
            "key_insights": ["Test"],
        }

        mock_client = MagicMock()
        response_mock = MagicMock()
        response_mock.text = json.dumps(invalid_response)
        mock_client.generate_content = MagicMock(return_value=response_mock)
        mock_google_generativeai.GenerativeModel.return_value = mock_client

        agent = PlanningAgent()

        with pytest.raises(PlanningError):
            await agent.analyze("test topic")

    @pytest.mark.asyncio
    async def test_analyze_empty_components_list(self, test_env, mock_google_generativeai):
        """Test analyze raises error when components list is empty."""
        invalid_response = {
            "concept": "Test",
            "diagram_type": "flowchart",
            "components": [],  # Empty
            "relationships": [],
            "success_criteria": ["Test"],
            "educational_level": "11-13",
            "key_insights": ["Test"],
        }

        mock_client = MagicMock()
        response_mock = MagicMock()
        response_mock.text = json.dumps(invalid_response)
        mock_client.generate_content = MagicMock(return_value=response_mock)
        mock_google_generativeai.GenerativeModel.return_value = mock_client

        agent = PlanningAgent()

        with pytest.raises(PlanningError):
            await agent.analyze("test topic")


class TestPlanningAgentParseJson:
    """Test JSON parsing functionality."""

    def test_parse_json_bare_json(self, test_env, mock_google_generativeai):
        """Test parsing bare JSON without markdown."""
        agent = PlanningAgent()

        json_text = '{"key": "value", "number": 42}'
        result = agent._parse_json_response(json_text)

        assert result["key"] == "value"
        assert result["number"] == 42

    def test_parse_json_with_markdown_code_block(self, test_env, mock_google_generativeai):
        """Test parsing JSON with ```json code block."""
        agent = PlanningAgent()

        json_text = """```json
{"key": "value", "nested": {"inner": "data"}}
```"""
        result = agent._parse_json_response(json_text)

        assert result["key"] == "value"
        assert result["nested"]["inner"] == "data"

    def test_parse_json_with_generic_code_block(self, test_env, mock_google_generativeai):
        """Test parsing JSON with generic ``` code block."""
        agent = PlanningAgent()

        json_text = """```
{"key": "value"}
```"""
        result = agent._parse_json_response(json_text)

        assert result["key"] == "value"

    def test_parse_json_with_whitespace(self, test_env, mock_google_generativeai):
        """Test parsing JSON with extra whitespace."""
        agent = PlanningAgent()

        json_text = """

```json
{"key": "value"}
```

  """
        result = agent._parse_json_response(json_text)

        assert result["key"] == "value"

    def test_parse_json_invalid_json(self, test_env, mock_google_generativeai):
        """Test parsing invalid JSON raises error."""
        agent = PlanningAgent()

        with pytest.raises(json.JSONDecodeError):
            agent._parse_json_response("not json")

    def test_parse_json_complex_structure(self, test_env, mock_google_generativeai):
        """Test parsing complex nested JSON."""
        agent = PlanningAgent()

        json_text = """```json
{
  "concept": "Photosynthesis",
  "components": ["A", "B", "C"],
  "relationships": [
    {"from": "A", "to": "B", "label": "leads"},
    {"from": "B", "to": "C", "label": "produces"}
  ],
  "nested": {
    "level2": {
      "level3": "value"
    }
  }
}
```"""
        result = agent._parse_json_response(json_text)

        assert result["concept"] == "Photosynthesis"
        assert len(result["components"]) == 3
        assert len(result["relationships"]) == 2
        assert result["nested"]["level2"]["level3"] == "value"


class TestPlanningAgentIntegration:
    """Integration tests for Planning Agent."""

    @pytest.mark.asyncio
    async def test_error_handling_cascade(self, test_env, mock_google_generativeai):
        """Test error is properly caught and re-raised as PlanningError."""
        mock_client = MagicMock()
        # Simulate API error
        mock_client.generate_content = MagicMock(
            side_effect=RuntimeError("API Connection failed")
        )
        mock_google_generativeai.GenerativeModel.return_value = mock_client

        agent = PlanningAgent()

        with pytest.raises(PlanningError, match="Failed to analyze concept"):
            await agent.analyze("test topic")
