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
                xml = await self._extract_xml_from_stream(response.text)
                if not xml:
                    logger.error("No XML content found in draw.io response")
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

        message = f"""Create an educational diagram for:

**Concept**: {plan.concept}
**Diagram Type**: {plan.diagram_type}
**Age Level**: {plan.educational_level}

**Components to include**:
{components_str}

**Relationships**:
{relationships_str}

**Key Teaching Points**:
{insights_str}

**Success Criteria**:
{criteria_str}

Generate a clear, pedagogically sound diagram using draw.io. The diagram should be appropriate for ages {plan.educational_level} and include all components with proper relationships shown."""

        return message

    async def _extract_xml_from_stream(self, response_text: str) -> str:
        """Extract XML from next-ai-draw-io streaming response.

        The streaming response contains multiple JSON chunks with tool results.
        We need to extract the XML content from display_diagram tool result.

        Args:
            response_text: Raw streaming response text

        Returns:
            Extracted XML string or None if not found
        """
        logger.debug(f"Parsing streaming response, length: {len(response_text)}")

        # Split by newlines to handle streaming format
        lines = response_text.strip().split("\n")
        xml_content = None

        for line in lines:
            if not line.strip():
                continue

            try:
                # Parse each line as JSON
                data = json.loads(line)

                # Look for display_diagram tool result with XML
                if isinstance(data, dict):
                    # Check if this is a tool-input with display_diagram
                    if (
                        data.get("type") == "tool-input-available"
                        and data.get("toolName") == "display_diagram"
                    ):
                        input_data = data.get("input", {})
                        if isinstance(input_data, dict) and "xml" in input_data:
                            xml_content = input_data["xml"]
                            logger.debug(
                                f"Found XML in tool-input-available, length: {len(xml_content)}"
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

        return xml_content
