# MCP Integration Implementation Plan

**Status**: Ready for Development
**Complexity**: Medium (2-3 hours)
**Risk Level**: Low (isolated change)
**Files to Modify**: 3 files

---

## Overview

This plan details how to refactor VisuaLearn's diagram generation to use next-ai-draw-io's MCP (Model Context Protocol) server instead of HTTP API calls.

**Key Change**: `diagram_generator.py` moves from HTTP requests to MCP tool calls

---

## Phase 1: Create MCP Client Wrapper

### File: `backend/app/services/mcp_client.py` (NEW)

**Purpose**: Abstract MCP communication details from diagram generator

```python
"""MCP Client for next-ai-draw-io integration."""

import asyncio
import json
import subprocess
import sys
from typing import Optional

from loguru import logger

from app.config import settings
from app.errors import GenerationError


class MCPError(Exception):
    """Base error for MCP communication"""
    pass


class MCPTimeoutError(MCPError):
    """MCP operation timed out"""
    pass


class MCPConnectionError(MCPError):
    """Cannot connect to MCP server"""
    pass


class MCPDiagramClient:
    """MCP client for diagram generation via next-ai-draw-io."""

    def __init__(self):
        """Initialize MCP client and start server process."""
        self.process: Optional[subprocess.Popen] = None
        self.timeout = settings.generation_timeout
        self._message_id = 0
        self._initialized = False

        logger.info("MCP client initialized")

    def _get_next_message_id(self) -> int:
        """Get next message ID for MCP requests."""
        self._message_id += 1
        return self._message_id

    def _start_server(self):
        """Start MCP server subprocess."""
        try:
            # Start next-ai-draw-io MCP server
            self.process = subprocess.Popen(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "run",
                    "npx @next-ai-drawio/mcp-server@latest",
                ],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,  # Line buffered
            )

            logger.info("MCP server process started", pid=self.process.pid)

        except FileNotFoundError as e:
            logger.error("Cannot start MCP server: npx not found")
            raise MCPConnectionError(
                "MCP server not available. Install with: npm install -g @next-ai-drawio/mcp-server"
            ) from e

    def _send_request(self, method: str, params: dict) -> dict:
        """Send MCP request and receive response."""
        if not self.process:
            self._start_server()

        msg_id = self._get_next_message_id()

        request = {
            "jsonrpc": "2.0",
            "id": msg_id,
            "method": method,
            "params": params,
        }

        try:
            # Send request
            request_str = json.dumps(request)
            self.process.stdin.write(request_str + "\n")
            self.process.stdin.flush()

            logger.debug(f"Sent MCP request: {method}")

            # Receive response with timeout
            response_str = None
            try:
                # Read response with timeout using asyncio
                loop = asyncio.get_event_loop()
                response_str = asyncio.run_coroutine_threadsafe(
                    self._read_response_async(),
                    loop,
                ).result(timeout=self.timeout)

            except subprocess.TimeoutExpired:
                logger.error(f"MCP request timed out after {self.timeout}s")
                raise MCPTimeoutError(f"MCP request timed out after {self.timeout}s")

            response = json.loads(response_str)

            if "error" in response:
                error_msg = response["error"].get("message", "Unknown error")
                logger.error(f"MCP error: {error_msg}")
                raise MCPError(f"MCP tool error: {error_msg}")

            logger.debug(f"Received MCP response for {method}")
            return response.get("result", {})

        except (BrokenPipeError, OSError) as e:
            logger.error(f"MCP server connection lost: {e}")
            self.process = None
            raise MCPConnectionError(f"MCP server connection lost: {e}") from e

    async def _read_response_async(self) -> str:
        """Read response from MCP server asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.process.stdout.readline)

    async def create_diagram(self, xml: str, title: Optional[str] = None) -> str:
        """Create a new diagram using MCP tool.

        Args:
            xml: draw.io XML diagram content
            title: Optional diagram title

        Returns:
            Generated diagram XML

        Raises:
            MCPError: If MCP operation fails
            MCPTimeoutError: If operation times out
        """
        logger.info("Creating diagram via MCP", title=title or "untitled")

        try:
            params = {"xml": xml}
            if title:
                params["title"] = title

            result = self._send_request("tools/call", {
                "name": "create_new_diagram",
                "arguments": params,
            })

            diagram_xml = result.get("xml")
            if not diagram_xml:
                raise MCPError("MCP tool returned no diagram XML")

            logger.info("Diagram created successfully via MCP")
            return diagram_xml

        except MCPError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in MCP create_diagram: {e}")
            raise MCPError(f"Failed to create diagram via MCP: {str(e)}") from e

    async def get_diagram(self, diagram_id: str) -> str:
        """Retrieve diagram XML by ID using MCP tool.

        Args:
            diagram_id: Diagram identifier

        Returns:
            Diagram XML content

        Raises:
            MCPError: If MCP operation fails
        """
        logger.info("Retrieving diagram via MCP", diagram_id=diagram_id)

        try:
            result = self._send_request("tools/call", {
                "name": "get_diagram",
                "arguments": {"diagram_id": diagram_id},
            })

            diagram_xml = result.get("xml")
            if not diagram_xml:
                raise MCPError(f"No diagram found with ID: {diagram_id}")

            return diagram_xml

        except MCPError:
            raise
        except Exception as e:
            logger.error(f"Error retrieving diagram via MCP: {e}")
            raise MCPError(f"Failed to retrieve diagram: {str(e)}") from e

    async def edit_diagram(
        self,
        diagram_id: str,
        operations: list[dict],
    ) -> str:
        """Edit existing diagram using MCP tool.

        Args:
            diagram_id: Diagram to edit
            operations: List of operations {add|update|delete} cells

        Returns:
            Updated diagram XML

        Raises:
            MCPError: If MCP operation fails
        """
        logger.info(
            "Editing diagram via MCP",
            diagram_id=diagram_id,
            operations_count=len(operations),
        )

        try:
            result = self._send_request("tools/call", {
                "name": "edit_diagram",
                "arguments": {
                    "diagram_id": diagram_id,
                    "operations": operations,
                },
            })

            updated_xml = result.get("xml")
            if not updated_xml:
                raise MCPError("MCP edit operation returned no diagram XML")

            return updated_xml

        except MCPError:
            raise
        except Exception as e:
            logger.error(f"Error editing diagram via MCP: {e}")
            raise MCPError(f"Failed to edit diagram: {str(e)}") from e

    def close(self):
        """Close MCP server connection."""
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
                logger.info("MCP server closed")
            except subprocess.TimeoutExpired:
                self.process.kill()
                logger.warning("MCP server killed (did not terminate gracefully)")

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        self.close()
```

**Key Design Decisions**:
- Uses subprocess to run MCP server
- JSON-RPC 2.0 protocol for communication
- Async/await support for integration with FastAPI
- Error handling for MCP-specific errors
- Logging for debugging

---

## Phase 2: Update DiagramGenerator

### File: `backend/app/services/diagram_generator.py` (MODIFY)

**Current Implementation** (lines 1-100):
```python
# OLD VERSION - HTTP-based
class DiagramGenerator:
    def __init__(self):
        self.timeout = settings.generation_timeout
        self.drawio_url = settings.drawio_service_url

    async def generate(self, plan: PlanningOutput) -> str:
        # Uses httpx to call HTTP API
        async with httpx.AsyncClient() as client:
            response = await client.post(...)
```

**New Implementation** (replace with):
```python
"""Diagram Generator service for creating draw.io XML diagrams."""

import asyncio
from typing import Optional

from loguru import logger

from app.config import settings
from app.errors import GenerationError
from app.services.mcp_client import MCPDiagramClient, MCPError, MCPTimeoutError
from app.services.planning_agent import PlanningOutput


class DiagramGenerator:
    """AI service for generating draw.io XML diagrams via MCP."""

    def __init__(self, use_mcp: bool = True):
        """Initialize diagram generator.

        Args:
            use_mcp: If True, use MCP client; if False, use HTTP (deprecated)
        """
        self.timeout = settings.generation_timeout
        self.use_mcp = use_mcp

        if use_mcp:
            self.mcp_client = MCPDiagramClient()
        else:
            # Keep HTTP fallback for migration period
            import httpx
            self.http_client = httpx.AsyncClient()

        logger.info(
            "Diagram generator initialized",
            mode="mcp" if use_mcp else "http",
        )

    async def generate(self, plan: PlanningOutput) -> str:
        """Generate diagram XML from planning specifications.

        Creates a draw.io format XML diagram based on the provided planning
        output using either MCP tool calls or HTTP API.

        Args:
            plan: PlanningOutput with diagram specifications

        Returns:
            draw.io XML string representing the diagram

        Raises:
            GenerationError: If generation fails or timeout occurs
        """
        logger.info(
            "Diagram generation started",
            concept=plan.concept,
            diagram_type=plan.diagram_type,
            mode="mcp" if self.use_mcp else "http",
        )

        try:
            if self.use_mcp:
                xml = await self._generate_via_mcp(plan)
            else:
                xml = await self._generate_via_http(plan)

            logger.info(
                "Diagram generation completed",
                concept=plan.concept,
                xml_length=len(xml),
                has_cells=xml.count("<mxCell") > 0,
            )

            return xml

        except GenerationError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in diagram generation: {e}")
            raise GenerationError(f"Failed to generate diagram: {str(e)}")

    async def _generate_via_mcp(self, plan: PlanningOutput) -> str:
        """Generate diagram using MCP tool.

        Args:
            plan: Planning output with diagram specifications

        Returns:
            draw.io XML string

        Raises:
            GenerationError: If MCP generation fails
        """
        try:
            # Create prompt for MCP to generate diagram
            prompt = self._create_generation_prompt(plan)

            logger.debug("Sending diagram generation to MCP", prompt_length=len(prompt))

            # Call MCP tool with timeout
            xml = await asyncio.wait_for(
                self.mcp_client.create_diagram(
                    xml=prompt,
                    title=plan.concept,
                ),
                timeout=self.timeout,
            )

            return xml

        except asyncio.TimeoutError:
            logger.error(f"MCP diagram generation timed out after {self.timeout}s")
            raise GenerationError(
                f"Diagram generation timed out after {self.timeout}s"
            )
        except MCPTimeoutError as e:
            logger.error(f"MCP timeout: {e}")
            raise GenerationError(f"Diagram generation timed out: {e}")
        except MCPError as e:
            logger.error(f"MCP error during generation: {e}")
            raise GenerationError(f"MCP generation failed: {e}")

    async def _generate_via_http(self, plan: PlanningOutput) -> str:
        """Generate diagram using HTTP API (deprecated fallback).

        Args:
            plan: Planning output with diagram specifications

        Returns:
            draw.io XML string

        Raises:
            GenerationError: If HTTP generation fails
        """
        # [Keep existing HTTP implementation for migration period]
        # This can be removed after successful MCP migration
        pass

    def _create_generation_prompt(self, plan: PlanningOutput) -> str:
        """Create XML prompt for diagram generation.

        Args:
            plan: Planning output with specifications

        Returns:
            Formatted prompt for MCP tool

        Raises:
            GenerationError: If prompt creation fails
        """
        try:
            # Create detailed generation prompt
            prompt = f"""
            Generate a {plan.diagram_type} diagram for: {plan.concept}

            Include these components:
            {chr(10).join(f'- {comp}' for comp in plan.components)}

            Include these relationships:
            {chr(10).join(f'- {rel["from"]} → {rel["to"]}: {rel.get("label", "")}' for rel in plan.relationships)}

            Success criteria:
            {chr(10).join(f'- {criteria}' for criteria in plan.success_criteria)}

            Key teaching points:
            {chr(10).join(f'- {insight}' for insight in plan.key_insights)}

            Educational level: {plan.educational_level}
            """

            logger.debug("Created generation prompt", length=len(prompt))
            return prompt

        except Exception as e:
            logger.error(f"Error creating generation prompt: {e}")
            raise GenerationError(f"Failed to create generation prompt: {e}")

    async def close(self):
        """Close connections."""
        if self.use_mcp and self.mcp_client:
            self.mcp_client.close()
        elif not self.use_mcp and self.http_client:
            await self.http_client.aclose()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
```

**Changes Made**:
1. Replace `httpx.AsyncClient` with `MCPDiagramClient`
2. Add `_generate_via_mcp()` method for MCP-based generation
3. Keep `_generate_via_http()` as fallback (can remove later)
4. Add MCP error handling
5. Update logging to show MCP vs HTTP mode

---

## Phase 3: Update Orchestrator

### File: `backend/app/services/orchestrator.py` (MINOR)

**Location**: Lines 80-90

**Current**:
```python
class Orchestrator:
    def __init__(self):
        """Initialize orchestrator with all required services."""
        self.planning_agent = PlanningAgent()
        self.diagram_generator = DiagramGenerator()  # HTTP mode
```

**Updated**:
```python
class Orchestrator:
    def __init__(self, use_mcp: bool = True):
        """Initialize orchestrator with all required services.

        Args:
            use_mcp: Use MCP client for diagram generation
        """
        self.planning_agent = PlanningAgent()
        self.diagram_generator = DiagramGenerator(use_mcp=use_mcp)  # MCP mode
```

**No other changes needed** - Orchestrator's orchestrate() method works unchanged.

---

## Phase 4: Configuration & Dependencies

### File: `backend/pyproject.toml` (MODIFY)

**Add MCP dependency**:
```toml
[project]
dependencies = [
    # ... existing dependencies ...
    "mcp>=0.1.0",  # Model Context Protocol
]
```

**No need to remove httpx** - We're keeping it as fallback during migration.

### File: `backend/.env` (UPDATE)

**Add MCP configuration** (optional):
```env
# MCP Configuration
USE_MCP_DIAGRAM_GENERATION=true
MCP_SERVER_PATH=@next-ai-drawio/mcp-server
```

---

## Phase 5: Testing Strategy

### File: `backend/tests/services/test_mcp_client.py` (NEW)

```python
"""Tests for MCP client."""

import pytest

from app.services.mcp_client import MCPDiagramClient, MCPError, MCPTimeoutError


@pytest.fixture
def mcp_client():
    """Create MCP client for testing."""
    return MCPDiagramClient()


@pytest.mark.asyncio
async def test_create_diagram_success(mcp_client):
    """Test successful diagram creation."""
    xml_input = "<mxfile><diagram><mxGraphModel></mxGraphModel></diagram></mxfile>"

    result = await mcp_client.create_diagram(xml_input, title="Test Diagram")

    assert result is not None
    assert "<mxCell" in result or "diagram" in result
    assert len(result) > 0


@pytest.mark.asyncio
async def test_create_diagram_with_timeout(mcp_client, monkeypatch):
    """Test diagram creation timeout."""
    xml_input = "<mxfile></mxfile>"

    # Mock timeout
    with pytest.raises(MCPTimeoutError):
        await mcp_client.create_diagram(xml_input)


@pytest.mark.asyncio
async def test_mcp_error_handling(mcp_client):
    """Test MCP error handling."""
    with pytest.raises(MCPError):
        await mcp_client.create_diagram("")  # Empty XML


def test_mcp_client_initialization():
    """Test MCP client initialization."""
    client = MCPDiagramClient()
    assert client is not None
    assert client.timeout > 0


def test_mcp_client_closes():
    """Test MCP client closes cleanly."""
    client = MCPDiagramClient()
    client.close()  # Should not raise
```

### File: `backend/tests/services/test_diagram_generator.py` (UPDATE)

**Add test for MCP mode**:
```python
@pytest.mark.asyncio
async def test_diagram_generator_mcp_mode():
    """Test diagram generator in MCP mode."""
    generator = DiagramGenerator(use_mcp=True)

    plan = PlanningOutput(
        concept="Test concept",
        diagram_type="flowchart",
        components=["A", "B", "C"],
        relationships=[{"from": "A", "to": "B", "label": "flows to"}],
        success_criteria=["All components connected"],
        key_insights=["Simple flow"],
    )

    xml = await generator.generate(plan)

    assert xml is not None
    assert len(xml) > 0
    assert "diagram" in xml.lower()

    await generator.close()
```

---

## Migration Strategy

### Option A: Gradual Rollout (Recommended)

```python
# backend/app/services/orchestrator.py
class Orchestrator:
    def __init__(self):
        # Start with MCP disabled
        use_mcp = settings.get("USE_MCP_DIAGRAM_GENERATION", False)

        self.diagram_generator = DiagramGenerator(use_mcp=use_mcp)
```

**Rollout stages**:
1. **Week 1**: Deploy with `USE_MCP_DIAGRAM_GENERATION=false` (no change)
2. **Week 2**: Enable for 10% of requests (monitoring)
3. **Week 3**: Enable for 50% of requests
4. **Week 4**: Enable 100% (complete migration)
5. **Week 5**: Remove HTTP fallback code

### Option B: Feature Flag

```python
# Create feature flag for A/B testing
import random

use_mcp = (
    settings.get("USE_MCP_DIAGRAM_GENERATION", False)
    or random.random() < settings.get("MCP_ROLLOUT_PERCENTAGE", 0.0)
)
```

---

## Rollback Plan

If MCP integration causes issues:

1. **Immediate**: Set `USE_MCP_DIAGRAM_GENERATION=false` in `.env`
2. **Revert**: Restart backend (will use HTTP fallback)
3. **Investigate**: Check logs for MCP errors
4. **Fix**: Deploy updated code
5. **Re-enable**: Gradually roll out again

---

## Success Criteria

- ✅ All tests pass (unit + integration)
- ✅ Performance: 80% latency reduction (150ms → 30ms)
- ✅ Error rate: <0.1% (same as HTTP)
- ✅ No API changes (frontend unaffected)
- ✅ Backward compatible (HTTP fallback works)

---

## Files Summary

| File | Action | Complexity |
|------|--------|------------|
| `app/services/mcp_client.py` | CREATE | High (250+ lines) |
| `app/services/diagram_generator.py` | MODIFY | Medium (update generate method) |
| `app/services/orchestrator.py` | MODIFY | Low (1 parameter) |
| `pyproject.toml` | MODIFY | Low (add 1 dependency) |
| `tests/services/test_mcp_client.py` | CREATE | Medium (50+ lines) |
| `tests/services/test_diagram_generator.py` | MODIFY | Low (add 1 test) |

---

## Timeline

- **Setup & Configuration**: 15 minutes
- **Create MCP Client**: 45 minutes
- **Refactor DiagramGenerator**: 30 minutes
- **Update Orchestrator**: 5 minutes
- **Write Tests**: 30 minutes
- **Testing & Validation**: 15 minutes
- **Documentation**: 10 minutes

**Total**: ~2-2.5 hours (including testing)

---

## Next Steps

1. ✅ Research complete - See `MCP_INTEGRATION_RESEARCH.md`
2. ⬜ Review this plan with team
3. ⬜ Implement Phase 1: Create MCP client
4. ⬜ Implement Phase 2: Update DiagramGenerator
5. ⬜ Implement Phase 3: Update Orchestrator
6. ⬜ Write and run tests
7. ⬜ Deploy with feature flag
8. ⬜ Monitor performance
9. ⬜ Gradual rollout
10. ⬜ Remove HTTP fallback

---

**Ready to proceed with implementation?**
