"""Diagram Generator service for creating draw.io XML diagrams via MCP."""

import asyncio
import json
import subprocess
import sys
from typing import Optional

from loguru import logger

from app.config import settings
from app.errors import GenerationError
from app.services.planning_agent import PlanningOutput


class DiagramGenerator:
    """AI service for generating draw.io XML diagrams via MCP protocol."""

    def __init__(self):
        """Initialize diagram generator with MCP service."""
        self.timeout = settings.generation_timeout
        self.mcp_process: Optional[subprocess.Popen] = None
        self._message_id = 0
        logger.info("Diagram generator initialized (MCP mode)")

    def _get_next_message_id(self) -> int:
        """Get next message ID for MCP requests."""
        self._message_id += 1
        return self._message_id

    def _ensure_mcp_server(self):
        """Ensure MCP server process is running."""
        if self.mcp_process is None or self.mcp_process.poll() is not None:
            logger.info("Starting MCP server subprocess")
            try:
                self.mcp_process = subprocess.Popen(
                    [sys.executable, "-m", "pip", "run", "npx", "@next-ai-drawio/mcp-server@latest"],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1,  # Line buffered
                )
                logger.info("MCP server started", pid=self.mcp_process.pid)
            except FileNotFoundError as e:
                logger.error("Cannot start MCP server - npx not found")
                raise GenerationError(
                    "MCP server unavailable. Install with: npm install -g @next-ai-drawio/mcp-server"
                ) from e

    async def generate(self, plan: PlanningOutput) -> str:
        """Generate diagram XML from planning specifications.

        Creates a draw.io format XML diagram using MCP protocol from next-ai-draw-io.

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
            components_count=len(plan.components),
        )

        try:
            # Run generation with timeout
            xml = await asyncio.wait_for(
                self._generate_via_mcp(plan),
                timeout=self.timeout,
            )
            logger.info(
                "Diagram generation completed",
                xml_length=len(xml),
                concept=plan.concept,
                mxcell_count=xml.count("<mxCell"),
            )
            return xml
        except asyncio.TimeoutError:
            logger.error(f"Diagram generation timed out after {self.timeout}s")
            raise GenerationError(
                f"Diagram generation timed out after {self.timeout}s"
            )
        except GenerationError:
            raise
        except Exception as e:
            logger.error(f"Diagram generation failed: {e}", exc_info=True)
            raise GenerationError(f"Failed to generate diagram: {str(e)}")

    async def _generate_via_mcp(self, plan: PlanningOutput) -> str:
        """Generate diagram using MCP tool call.

        Args:
            plan: PlanningOutput with diagram specifications

        Returns:
            draw.io XML string

        Raises:
            GenerationError: If MCP generation fails
        """
        # Ensure MCP server is running
        self._ensure_mcp_server()

        # Create user message from planning output
        user_message = self._create_user_message(plan)

        # Build MCP request
        msg_id = self._get_next_message_id()
        mcp_request = {
            "jsonrpc": "2.0",
            "id": msg_id,
            "method": "tools/call",
            "params": {
                "name": "create_new_diagram",
                "arguments": {
                    "xml": user_message,
                    "title": plan.concept,
                },
            },
        }

        logger.debug("Sending MCP tool call", method="create_new_diagram", msg_id=msg_id)

        try:
            # Send request to MCP server
            request_str = json.dumps(mcp_request)
            self.mcp_process.stdin.write(request_str + "\n")
            self.mcp_process.stdin.flush()

            # Read response with timeout
            loop = asyncio.get_event_loop()
            response_str = await asyncio.wait_for(
                loop.run_in_executor(None, self.mcp_process.stdout.readline),
                timeout=self.timeout,
            )

            if not response_str:
                logger.error("MCP server closed unexpectedly")
                self.mcp_process = None  # Reset for next attempt
                raise GenerationError("MCP server connection lost")

            response = json.loads(response_str)

            # Check for errors in response
            if "error" in response:
                error_msg = response["error"].get("message", "Unknown MCP error")
                logger.error(f"MCP error: {error_msg}")
                raise GenerationError(f"MCP diagram generation failed: {error_msg}")

            # Extract XML from result
            result = response.get("result", {})
            xml = result.get("xml")

            if not xml:
                logger.error("MCP tool returned no XML", result=result)
                raise GenerationError("MCP tool returned empty diagram")

            logger.debug("MCP diagram generated", xml_length=len(xml))
            return xml

        except asyncio.TimeoutError:
            logger.error(f"MCP request timed out after {self.timeout}s")
            raise GenerationError(f"Diagram generation timed out after {self.timeout}s")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse MCP response: {e}")
            raise GenerationError(f"Invalid MCP response format: {e}")
        except (BrokenPipeError, OSError) as e:
            logger.error(f"MCP server connection lost: {e}")
            self.mcp_process = None  # Reset for next attempt
            raise GenerationError(f"MCP server connection failed: {e}")
        except Exception as e:
            logger.error(f"MCP generation error: {e}", exc_info=True)
            raise GenerationError(f"MCP diagram generation failed: {str(e)}")

    def _create_user_message(self, plan: PlanningOutput) -> str:
        """Create a structured prompt from planning output for MCP tool.

        Args:
            plan: PlanningOutput with diagram specifications

        Returns:
            Formatted prompt for the MCP create_new_diagram tool
        """
        components_str = "\n".join(f"  - {c}" for c in plan.components)
        relationships_str = "\n".join(
            f"  - {r['from']} → {r['to']}: {r.get('label', '')}" for r in plan.relationships
        )
        insights_str = "\n".join(f"  - {i}" for i in plan.key_insights)
        criteria_str = "\n".join(f"  - {c}" for c in plan.success_criteria)

        message = f"""Create a COMPLETE educational diagram with ALL components and relationships for:

**Concept**: {plan.concept}
**Diagram Type**: {plan.diagram_type}

**MUST INCLUDE All These Components** ({len(plan.components)} total):
{components_str}

**MUST INCLUDE All These Relationships** ({len(plan.relationships)} total):
{relationships_str}

**Key Teaching Points**:
{insights_str}

**Success Criteria**:
{criteria_str}

REQUIREMENTS:
1. Create a {plan.diagram_type} diagram
2. Include ALL {len(plan.components)} components listed above
3. Show ALL {len(plan.relationships)} relationships between components
4. Use clear, readable labels
5. Apply appropriate shapes and colors for visual clarity
6. Return complete draw.io XML with proper structure

Generate a clear, complete, pedagogically sound educational diagram."""

        return message
