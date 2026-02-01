"""Tests for Diagram Generator service."""

import asyncio
import json
import subprocess
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.errors import GenerationError
from app.services.diagram_generator import DiagramGenerator
from app.services.planning_agent import PlanningOutput


class TestDiagramGeneratorInit:
    """Test DiagramGenerator initialization."""

    def test_init_creates_generator(self, test_env):
        """Test successful initialization creates generator with MCP setup."""
        generator = DiagramGenerator()
        assert generator.timeout > 0  # Should have a timeout set
        assert generator.mcp_process is None  # No process until first use
        assert generator._message_id == 0
        assert hasattr(generator, '_ensure_mcp_server')
        assert hasattr(generator, '_generate_via_mcp')
        assert hasattr(generator, '_get_next_message_id')


class TestDiagramGeneratorMessageId:
    """Test message ID tracking for JSON-RPC."""

    def test_get_next_message_id_increments(self):
        """Test message ID increments correctly."""
        generator = DiagramGenerator()

        assert generator._get_next_message_id() == 1
        assert generator._get_next_message_id() == 2
        assert generator._get_next_message_id() == 3
        assert generator._message_id == 3

    def test_multiple_generators_have_separate_ids(self):
        """Test each generator instance has separate message IDs."""
        gen1 = DiagramGenerator()
        gen2 = DiagramGenerator()

        assert gen1._get_next_message_id() == 1
        assert gen2._get_next_message_id() == 1
        assert gen1._get_next_message_id() == 2
        assert gen2._get_next_message_id() == 2


class TestDiagramGeneratorMCPServer:
    """Test MCP server lifecycle management."""

    def test_ensure_mcp_server_starts_process(self, monkeypatch):
        """Test _ensure_mcp_server starts subprocess."""
        mock_process = MagicMock()
        mock_process.poll = MagicMock(return_value=None)

        mock_popen = MagicMock(return_value=mock_process)
        monkeypatch.setattr("app.services.diagram_generator.subprocess.Popen", mock_popen)

        generator = DiagramGenerator()
        generator._ensure_mcp_server()

        # Verify Popen was called
        assert mock_popen.called
        # Verify process is stored
        assert generator.mcp_process == mock_process

    def test_ensure_mcp_server_does_not_restart_running_process(self, monkeypatch):
        """Test _ensure_mcp_server reuses running process."""
        mock_process = MagicMock()
        mock_process.poll = MagicMock(return_value=None)  # Process is running

        generator = DiagramGenerator()
        generator.mcp_process = mock_process

        call_count = 0
        def mock_popen(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            return MagicMock()

        monkeypatch.setattr("app.services.diagram_generator.subprocess.Popen", mock_popen)

        generator._ensure_mcp_server()

        # Should not create new process
        assert call_count == 0
        assert generator.mcp_process == mock_process

    def test_ensure_mcp_server_restarts_dead_process(self, monkeypatch):
        """Test _ensure_mcp_server restarts dead process."""
        dead_process = MagicMock()
        dead_process.poll = MagicMock(return_value=1)  # Process is dead

        new_process = MagicMock()
        new_process.poll = MagicMock(return_value=None)

        mock_popen = MagicMock(return_value=new_process)
        monkeypatch.setattr("app.services.diagram_generator.subprocess.Popen", mock_popen)

        generator = DiagramGenerator()
        generator.mcp_process = dead_process

        generator._ensure_mcp_server()

        # Should create new process
        assert generator.mcp_process == new_process

    def test_ensure_mcp_server_raises_on_missing_npx(self, monkeypatch):
        """Test _ensure_mcp_server raises error if npx not found."""
        def mock_popen(*args, **kwargs):
            raise FileNotFoundError("npx not found")

        monkeypatch.setattr("app.services.diagram_generator.subprocess.Popen", mock_popen)

        generator = DiagramGenerator()

        with pytest.raises(GenerationError, match="MCP server unavailable"):
            generator._ensure_mcp_server()


class TestDiagramGeneratorGenerate:
    """Test DiagramGenerator.generate() method."""

    @pytest.mark.asyncio
    async def test_generate_timeout(self, test_env, monkeypatch):
        """Test generate raises timeout error."""

        async def slow_generation(*args, **kwargs):
            await asyncio.sleep(10)

        generator = DiagramGenerator()
        generator.timeout = 0.001  # Set very short timeout
        generator._generate_via_mcp = slow_generation

        plan = PlanningOutput(
            concept="Test",
            diagram_type="flowchart",
            components=["A"],
            relationships=[],
            success_criteria=["Test"],
            key_insights=["Test"],
        )

        with pytest.raises(GenerationError, match="timed out"):
            await generator.generate(plan)

    @pytest.mark.asyncio
    async def test_generate_with_valid_mcp_response(self, test_env, monkeypatch, mock_mcp_process):
        """Test generate with valid MCP response containing XML."""

        def mock_popen(*args, **kwargs):
            return mock_mcp_process

        monkeypatch.setattr("app.services.diagram_generator.subprocess.Popen", mock_popen)

        # Mock the executor to return the MCP process response
        async def mock_executor_read(*args, **kwargs):
            # Simulate reading from stdout
            mcp_response = {
                "jsonrpc": "2.0",
                "id": 1,
                "result": {
                    "xml": "<mxfile><diagram>Test</diagram></mxfile>"
                }
            }
            return json.dumps(mcp_response)

        generator = DiagramGenerator()
        plan = PlanningOutput(
            concept="Test",
            diagram_type="flowchart",
            components=["A"],
            relationships=[],
            success_criteria=["Test"],
            key_insights=["Test"],
        )

        with patch("asyncio.get_event_loop") as mock_loop:
            loop_instance = MagicMock()
            mock_loop.return_value = loop_instance
            loop_instance.run_in_executor = AsyncMock(
                return_value=json.dumps({
                    "jsonrpc": "2.0",
                    "id": 1,
                    "result": {"xml": "<mxfile><diagram>Test</diagram></mxfile>"}
                })
            )

            result = await generator.generate(plan)
            assert "<mxfile>" in result
            assert "Test" in result

    @pytest.mark.asyncio
    async def test_generate_mcp_server_closed(self, test_env, monkeypatch):
        """Test generate handles MCP server closing unexpectedly."""

        mock_process = MagicMock()
        mock_process.poll = MagicMock(return_value=None)
        mock_process.stdin = MagicMock()
        mock_process.stdin.write = MagicMock()
        mock_process.stdin.flush = MagicMock()
        mock_process.stdout = MagicMock()

        def mock_popen(*args, **kwargs):
            return mock_process

        monkeypatch.setattr("app.services.diagram_generator.subprocess.Popen", mock_popen)

        async def mock_executor_read(*args, **kwargs):
            return ""  # Empty response means connection closed

        generator = DiagramGenerator()
        plan = PlanningOutput(
            concept="Test",
            diagram_type="flowchart",
            components=["A"],
            relationships=[],
            success_criteria=["Test"],
            key_insights=["Test"],
        )

        with patch("asyncio.get_event_loop") as mock_loop:
            loop_instance = MagicMock()
            mock_loop.return_value = loop_instance
            loop_instance.run_in_executor = AsyncMock(
                side_effect=mock_executor_read
            )

            with pytest.raises(GenerationError, match="connection lost"):
                await generator.generate(plan)

    @pytest.mark.asyncio
    async def test_generate_mcp_error_response(self, test_env, monkeypatch, mock_mcp_process_error):
        """Test generate handles MCP error responses."""

        def mock_popen(*args, **kwargs):
            return mock_mcp_process_error

        monkeypatch.setattr("app.services.diagram_generator.subprocess.Popen", mock_popen)

        async def mock_executor_read(*args, **kwargs):
            mcp_response = {
                "jsonrpc": "2.0",
                "id": 1,
                "error": {
                    "code": -32603,
                    "message": "MCP tool execution failed"
                }
            }
            return json.dumps(mcp_response)

        generator = DiagramGenerator()
        plan = PlanningOutput(
            concept="Test",
            diagram_type="flowchart",
            components=["A"],
            relationships=[],
            success_criteria=["Test"],
            key_insights=["Test"],
        )

        with patch("asyncio.get_event_loop") as mock_loop:
            loop_instance = MagicMock()
            mock_loop.return_value = loop_instance
            loop_instance.run_in_executor = AsyncMock(
                side_effect=mock_executor_read
            )

            with pytest.raises(GenerationError, match="MCP diagram generation failed"):
                await generator.generate(plan)

    @pytest.mark.asyncio
    async def test_generate_invalid_json_response(self, test_env, monkeypatch):
        """Test generate handles invalid JSON from MCP."""

        mock_process = MagicMock()
        mock_process.poll = MagicMock(return_value=None)
        mock_process.stdin = MagicMock()
        mock_process.stdin.write = MagicMock()
        mock_process.stdin.flush = MagicMock()

        def mock_popen(*args, **kwargs):
            return mock_process

        monkeypatch.setattr("app.services.diagram_generator.subprocess.Popen", mock_popen)

        async def mock_executor_read(*args, **kwargs):
            return "invalid json {"  # Not valid JSON

        generator = DiagramGenerator()
        plan = PlanningOutput(
            concept="Test",
            diagram_type="flowchart",
            components=["A"],
            relationships=[],
            success_criteria=["Test"],
            key_insights=["Test"],
        )

        with patch("asyncio.get_event_loop") as mock_loop:
            loop_instance = MagicMock()
            mock_loop.return_value = loop_instance
            loop_instance.run_in_executor = AsyncMock(
                side_effect=mock_executor_read
            )

            with pytest.raises(GenerationError, match="Invalid MCP response format"):
                await generator.generate(plan)

    @pytest.mark.asyncio
    async def test_generate_no_xml_in_response(self, test_env, monkeypatch):
        """Test generate when response has no XML content."""

        mock_process = MagicMock()
        mock_process.poll = MagicMock(return_value=None)
        mock_process.stdin = MagicMock()
        mock_process.stdin.write = MagicMock()
        mock_process.stdin.flush = MagicMock()

        def mock_popen(*args, **kwargs):
            return mock_process

        monkeypatch.setattr("app.services.diagram_generator.subprocess.Popen", mock_popen)

        async def mock_executor_read(*args, **kwargs):
            # Response without XML
            mcp_response = {
                "jsonrpc": "2.0",
                "id": 1,
                "result": {}
            }
            return json.dumps(mcp_response)

        generator = DiagramGenerator()
        plan = PlanningOutput(
            concept="Test",
            diagram_type="flowchart",
            components=["A"],
            relationships=[],
            success_criteria=["Test"],
            key_insights=["Test"],
        )

        with patch("asyncio.get_event_loop") as mock_loop:
            loop_instance = MagicMock()
            mock_loop.return_value = loop_instance
            loop_instance.run_in_executor = AsyncMock(
                side_effect=mock_executor_read
            )

            with pytest.raises(GenerationError, match="empty diagram"):
                await generator.generate(plan)


class TestDiagramGeneratorSuccess:
    """Test successful diagram generation."""

    @pytest.mark.asyncio
    async def test_generate_success_simple_plan(self, test_env, monkeypatch):
        """Test successful generation with simple plan."""
        valid_xml = "<mxfile><diagram>Test</diagram></mxfile>"

        mock_process = MagicMock()
        mock_process.poll = MagicMock(return_value=None)
        mock_process.stdin = MagicMock()
        mock_process.stdin.write = MagicMock()
        mock_process.stdin.flush = MagicMock()

        def mock_popen(*args, **kwargs):
            return mock_process

        monkeypatch.setattr("app.services.diagram_generator.subprocess.Popen", mock_popen)

        async def mock_executor_read(*args, **kwargs):
            mcp_response = {
                "jsonrpc": "2.0",
                "id": 1,
                "result": {
                    "xml": valid_xml
                }
            }
            return json.dumps(mcp_response)

        generator = DiagramGenerator()
        plan = PlanningOutput(
            concept="Test",
            diagram_type="flowchart",
            components=["A"],
            relationships=[],
            success_criteria=["Test"],
            key_insights=["Test"],
        )

        with patch("asyncio.get_event_loop") as mock_loop:
            loop_instance = MagicMock()
            mock_loop.return_value = loop_instance
            loop_instance.run_in_executor = AsyncMock(
                side_effect=mock_executor_read
            )

            result = await generator.generate(plan)
            assert result == valid_xml

    @pytest.mark.asyncio
    async def test_generate_success_complex_plan(self, test_env, monkeypatch):
        """Test generation with complex planning output."""
        valid_xml = "<mxfile><diagram>Complex</diagram></mxfile>"

        mock_process = MagicMock()
        mock_process.poll = MagicMock(return_value=None)
        mock_process.stdin = MagicMock()
        mock_process.stdin.write = MagicMock()
        mock_process.stdin.flush = MagicMock()

        def mock_popen(*args, **kwargs):
            return mock_process

        monkeypatch.setattr("app.services.diagram_generator.subprocess.Popen", mock_popen)

        async def mock_executor_read(*args, **kwargs):
            mcp_response = {
                "jsonrpc": "2.0",
                "id": 1,
                "result": {
                    "xml": valid_xml
                }
            }
            return json.dumps(mcp_response)

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
            key_insights=["Plants make food", "Sunlight is energy source"],
        )

        with patch("asyncio.get_event_loop") as mock_loop:
            loop_instance = MagicMock()
            mock_loop.return_value = loop_instance
            loop_instance.run_in_executor = AsyncMock(
                side_effect=mock_executor_read
            )

            result = await generator.generate(plan)
            assert result == valid_xml

    @pytest.mark.asyncio
    async def test_generate_sends_correct_json_rpc_request(self, test_env, monkeypatch):
        """Test generate sends properly formatted JSON-RPC request."""
        valid_xml = "<mxfile><diagram>Test</diagram></mxfile>"

        mock_process = MagicMock()
        mock_process.poll = MagicMock(return_value=None)
        mock_process.stdin = MagicMock()
        mock_process.stdin.write = MagicMock()
        mock_process.stdin.flush = MagicMock()

        write_calls = []
        def capture_write(data):
            write_calls.append(data)

        mock_process.stdin.write.side_effect = capture_write

        def mock_popen(*args, **kwargs):
            return mock_process

        monkeypatch.setattr("app.services.diagram_generator.subprocess.Popen", mock_popen)

        async def mock_executor_read(*args, **kwargs):
            mcp_response = {
                "jsonrpc": "2.0",
                "id": 1,
                "result": {"xml": valid_xml}
            }
            return json.dumps(mcp_response)

        generator = DiagramGenerator()
        plan = PlanningOutput(
            concept="Test",
            diagram_type="flowchart",
            components=["A"],
            relationships=[],
            success_criteria=["Test"],
            key_insights=["Test"],
        )

        with patch("asyncio.get_event_loop") as mock_loop:
            loop_instance = MagicMock()
            mock_loop.return_value = loop_instance
            loop_instance.run_in_executor = AsyncMock(
                side_effect=mock_executor_read
            )

            await generator.generate(plan)

            # Verify stdin.write was called with proper JSON-RPC request
            assert len(write_calls) > 0
            request_str = write_calls[0]
            # Remove trailing newline if present
            if request_str.endswith("\n"):
                request_str = request_str[:-1]
            request = json.loads(request_str)

            assert request["jsonrpc"] == "2.0"
            assert request["id"] == 1
            assert request["method"] == "tools/call"
            assert request["params"]["name"] == "create_new_diagram"
            assert "xml" in request["params"]["arguments"]
            assert "title" in request["params"]["arguments"]
            assert request["params"]["arguments"]["title"] == "Test"


class TestDiagramGeneratorIntegration:
    """Integration tests for Diagram Generator."""

    @pytest.mark.asyncio
    async def test_mcp_server_lifecycle_in_generate(self, test_env, monkeypatch):
        """Test MCP server is started and reused across calls."""
        valid_xml = "<mxfile><diagram>Test</diagram></mxfile>"

        process_count = 0
        mock_processes = []

        def mock_popen(*args, **kwargs):
            nonlocal process_count
            process_count += 1
            mock_process = MagicMock()
            mock_process.pid = process_count
            mock_process.poll = MagicMock(return_value=None)
            mock_process.stdin = MagicMock()
            mock_process.stdin.write = MagicMock()
            mock_process.stdin.flush = MagicMock()
            mock_processes.append(mock_process)
            return mock_process

        monkeypatch.setattr("app.services.diagram_generator.subprocess.Popen", mock_popen)

        async def mock_executor_read(*args, **kwargs):
            mcp_response = {
                "jsonrpc": "2.0",
                "id": 1,
                "result": {"xml": valid_xml}
            }
            return json.dumps(mcp_response)

        generator = DiagramGenerator()
        plan = PlanningOutput(
            concept="Test",
            diagram_type="flowchart",
            components=["A"],
            relationships=[],
            success_criteria=["Test"],
            key_insights=["Test"],
        )

        with patch("asyncio.get_event_loop") as mock_loop:
            loop_instance = MagicMock()
            mock_loop.return_value = loop_instance
            loop_instance.run_in_executor = AsyncMock(
                side_effect=mock_executor_read
            )

            # First call should start process
            await generator.generate(plan)
            assert process_count == 1

            # Second call should reuse same process
            await generator.generate(plan)
            assert process_count == 1

    @pytest.mark.asyncio
    async def test_error_handling_broken_pipe(self, test_env, monkeypatch):
        """Test error handling when MCP process pipe is broken."""

        mock_process = MagicMock()
        mock_process.poll = MagicMock(return_value=None)
        mock_process.stdin = MagicMock()
        mock_process.stdin.write = MagicMock(side_effect=BrokenPipeError("Pipe broken"))
        mock_process.stdin.flush = MagicMock()

        def mock_popen(*args, **kwargs):
            return mock_process

        monkeypatch.setattr("app.services.diagram_generator.subprocess.Popen", mock_popen)

        generator = DiagramGenerator()
        plan = PlanningOutput(
            concept="Test",
            diagram_type="flowchart",
            components=["A"],
            relationships=[],
            success_criteria=["Test"],
            key_insights=["Test"],
        )

        with pytest.raises(GenerationError, match="connection failed"):
            await generator.generate(plan)

        # Process should be reset for next attempt
        assert generator.mcp_process is None
