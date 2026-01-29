"""Diagram Generator service for creating draw.io XML diagrams."""

import asyncio
import json

import httpx
from loguru import logger

from app.config import settings
from app.errors import GenerationError
from app.services.planning_agent import PlanningOutput


class DiagramGenerator:
    """AI service for generating draw.io XML diagrams via next-ai-draw-io."""

    def __init__(self):
        """Initialize diagram generator with service configuration."""
        self.timeout = settings.generation_timeout
        self.drawio_url = settings.drawio_service_url

    async def generate(self, plan: PlanningOutput) -> str:
        """Generate diagram XML from planning specifications.

        Creates a draw.io format XML diagram based on the provided planning
        output using the next-ai-draw-io chat API with streaming.

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
                self._generate_internal(plan),
                timeout=self.timeout,
            )
            logger.info(
                "Diagram generation completed",
                xml_length=len(xml),
                concept=plan.concept,
            )
            return xml
        except asyncio.TimeoutError:
            logger.error(f"Diagram generation timed out after {self.timeout}s")
            raise GenerationError(
                f"Diagram generation timed out after {self.timeout}s."
            )
        except GenerationError:
            # Re-raise GenerationErrors as-is
            raise
        except Exception as e:
            logger.error(f"Diagram generation failed: {e}")
            raise GenerationError(f"Failed to generate diagram: {str(e)}")

    async def _generate_internal(self, plan: PlanningOutput) -> str:
        """Internal generation implementation via next-ai-draw-io chat API.

        Calls the streaming /api/chat endpoint and extracts XML from response.

        Args:
            plan: PlanningOutput with diagram specifications

        Returns:
            draw.io XML string

        Raises:
            GenerationError: If generation fails
        """
        # Create user message from planning output
        user_message = self._create_user_message(plan)

        # Prepare request payload for next-ai-draw-io chat API
        payload = {
            "messages": [
                {
                    "role": "user",
                    "parts": [{"type": "text", "text": user_message}],
                }
            ],
            "xml": "",  # Empty initial XML
            "previousXml": "",  # No previous diagram
        }

        logger.debug(f"Sending request to {self.drawio_url}/api/chat")

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.drawio_url}/api/chat",
                    json=payload,
                )

                if response.status_code != 200:
                    logger.error(
                        f"Draw.io service error: {response.status_code}",
                        response_text=response.text[:500],
                    )
                    raise GenerationError(
                        f"Draw.io service returned {response.status_code}: {response.text[:200]}"
                    )

                # Parse streaming response to extract XML
                logger.debug(
                    "Raw response received",
                    response_length=len(response.text),
                    lines_count=len(response.text.split('\n')),
                )
                xml = await self._extract_xml_from_stream(response.text)
                logger.debug(
                    "XML extraction result",
                    xml_length=len(xml) if xml else 0,
                    xml_cells=xml.count("<mxCell") if xml else 0,
                )
                if not xml:
                    logger.error(
                        "No XML content found in draw.io response",
                        response_preview=response.text[:1000],
                    )
                    raise GenerationError(
                        "Failed to extract diagram from draw.io response"
                    )

                logger.debug(f"Generated XML length: {len(xml)}")
                return xml

        except asyncio.TimeoutError:
            logger.error(f"Diagram generation timed out after {self.timeout}s")
            raise GenerationError(
                f"Diagram generation timed out after {self.timeout}s"
            )
        except httpx.ConnectError as e:
            logger.error(f"Cannot connect to diagram service at {self.drawio_url}: {e}")
            raise GenerationError(
                f"Cannot connect to diagram service. Is it running at {self.drawio_url}?"
            )
        except GenerationError:
            raise
        except Exception as e:
            logger.error(f"Diagram generation failed: {e}")
            raise GenerationError(f"Failed to generate diagram: {str(e)}")

    def _create_user_message(self, plan: PlanningOutput) -> str:
        """Create a structured prompt from planning output.

        Args:
            plan: PlanningOutput with diagram specifications

        Returns:
            Formatted user message for the chat API
        """
        components_str = "\n".join(f"  - {c}" for c in plan.components)
        relationships_str = "\n".join(
            f"  - {r['from']} → {r['to']}: {r['label']}" for r in plan.relationships
        )
        insights_str = "\n".join(f"  - {i}" for i in plan.key_insights)
        criteria_str = "\n".join(f"  - {c}" for c in plan.success_criteria)

        message = f"""Create a COMPLETE educational diagram with ALL components and relationships for:

**Concept**: {plan.concept}
**Diagram Type**: {plan.diagram_type}
**Age Level**: {plan.educational_level}

**MUST INCLUDE All These Components** (total: {len(plan.components)}):
{components_str}

**MUST INCLUDE All These Relationships** (total: {len(plan.relationships)}):
{relationships_str}

**Key Teaching Points**:
{insights_str}

**Success Criteria**:
{criteria_str}

IMPORTANT:
1. Include EVERY component listed above in the diagram
2. Show ALL relationships between components
3. Make labels clear and readable
4. Use appropriate shapes and colors for visual clarity
5. Return complete draw.io XML with ALL mxCell elements

Generate a clear, complete, pedagogically sound diagram using draw.io. The diagram must include all {len(plan.components)} components with all {len(plan.relationships)} relationships shown. The diagram should be appropriate for ages {plan.educational_level}."""

        return message

    async def _extract_xml_from_stream(self, response_text: str) -> str:
        """Extract XML from next-ai-draw-io streaming response.

        The streaming response is in Server-Sent Events (SSE) format with
        multiple JSON chunks. Each line starts with "data: " and contains JSON.
        We need to extract the XML content from display_diagram tool result.

        Args:
            response_text: Raw streaming response text in SSE format

        Returns:
            Extracted XML string or None if not found
        """
        logger.debug(f"Parsing streaming response, length: {len(response_text)}")

        # Split by newlines to handle streaming format
        lines = response_text.strip().split("\n")
        xml_content = None
        event_count = 0

        for line in lines:
            if not line.strip():
                continue

            # Handle Server-Sent Events (SSE) format with "data: " prefix
            json_str = line
            if json_str.startswith("data: "):
                json_str = json_str[6:]  # Remove "data: " prefix

            try:
                # Parse each line as JSON
                data = json.loads(json_str)
                event_count += 1

                # Look for display_diagram tool result with XML
                if isinstance(data, dict):
                    # Check if this is a tool-input-available with display_diagram
                    if (
                        data.get("type") == "tool-input-available"
                        and data.get("toolName") == "display_diagram"
                    ):
                        input_data = data.get("input", {})
                        if isinstance(input_data, dict) and "xml" in input_data:
                            xml_content = input_data["xml"]
                            cell_count = xml_content.count("<mxCell")
                            logger.debug(
                                f"Found XML in tool-input-available",
                                xml_length=len(xml_content),
                                cell_count=cell_count,
                                event_index=event_count,
                            )
                            break

            except json.JSONDecodeError:
                # This line might not be valid JSON, continue
                continue

        if not xml_content:
            logger.warning(
                "Could not extract XML from streaming response, trying direct parse"
            )
            # Fallback: try to find XML directly in response
            if "<mxfile" in response_text:
                start = response_text.find("<mxfile")
                end = response_text.rfind("</mxfile>")
                if start >= 0 and end > start:
                    xml_content = response_text[start : end + 9]

        # Wrap cell fragments in proper draw.io structure if needed
        if xml_content and not xml_content.strip().startswith("<mxfile"):
            cell_count = xml_content.count("<mxCell")
            logger.debug(
                f"Wrapping cell fragments in mxfile structure",
                fragment_length=len(xml_content),
                cell_count=cell_count,
            )
            # Validate we have a reasonable number of cells before wrapping
            if cell_count < 2:
                logger.warning(
                    f"Very few cells in XML ({cell_count}), response might be incomplete",
                    xml_preview=xml_content[:500],
                )
            xml_content = self._wrap_cells_in_mxfile(xml_content)

        return xml_content

    def _wrap_cells_in_mxfile(self, cells_xml: str) -> str:
        """Wrap raw cell XML in a proper draw.io mxfile structure.

        Next-ai-draw-io returns only the cell elements. We need to wrap them
        in the proper draw.io XML structure with mxfile, diagram, mxGraphModel, and root.

        Args:
            cells_xml: Raw cell XML fragments from the API

        Returns:
            Complete draw.io XML with proper structure
        """
        # Wrap in proper draw.io structure
        wrapped = f"""<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="drawio" modified="2024-01-01T00:00:00Z" agent="VisuaLearn" version="1.0">
  <diagram name="Diagram">
    <mxGraphModel dx="1200" dy="800" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="850" pageHeight="1100" math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        {cells_xml}
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>"""
        return wrapped
