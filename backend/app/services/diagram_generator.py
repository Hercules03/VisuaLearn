"""Diagram Generator service for creating draw.io XML diagrams."""

import asyncio
import json

import httpx
from loguru import logger

from app.config import settings
from app.errors import GenerationError
from app.services.planning_agent import PlanningOutput


class DiagramGenerator:
    """AI service for generating draw.io XML diagrams."""

    def __init__(self):
        """Initialize diagram generator with configuration."""
        self.timeout = settings.generation_timeout
        self.drawio_url = settings.drawio_service_url
        logger.info(
            "Diagram generator initialized",
            url=self.drawio_url,
            timeout=self.timeout,
        )

    async def generate(self, plan: PlanningOutput) -> str:
        """Generate diagram XML from planning specifications.

        Creates a draw.io format XML diagram based on the provided planning
        output using the next-ai-draw-io service.

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
        """Internal generation implementation using next-ai-draw-io.

        Args:
            plan: PlanningOutput with diagram specifications

        Returns:
            draw.io XML string

        Raises:
            GenerationError: If generation or API call fails
        """
        # Create prompt for diagram generation
        prompt = f"""Create a detailed {plan.diagram_type} diagram in draw.io format for the following educational concept.

Concept: {plan.concept}
Target Age Group: {plan.educational_level}

Elements to Include:
{chr(10).join(f"- {component}" for component in plan.components)}

Relationships Between Elements:
{chr(10).join(f"- {rel['from']} -> {rel['to']}: {rel['label']}" for rel in plan.relationships)}

Key Teaching Points:
{chr(10).join(f"- {insight}" for insight in plan.key_insights)}

Requirements:
1. Create a clear, educational {plan.diagram_type}
2. Include all specified elements with proper labels
3. Show relationships clearly
4. Use appropriate colors and styling for {plan.educational_level}
5. Ensure the diagram is pedagogically sound
6. Output ONLY valid draw.io XML, no markdown or code blocks"""

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Call next-ai-draw-io service
                response = await client.post(
                    f"{self.drawio_url}/api/diagram",
                    json={"prompt": prompt, "format": "xml"},
                )

                if response.status_code != 200:
                    logger.error(
                        f"Draw.io service error: {response.status_code}",
                        response_text=response.text[:500],
                    )
                    raise GenerationError(
                        f"Draw.io service returned {response.status_code}: {response.text[:200]}"
                    )

                # Parse response
                try:
                    result = response.json()
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse draw.io response: {e}")
                    raise GenerationError(
                        f"Invalid JSON response from draw.io service: {e}"
                    )

                # Extract XML from response
                xml = result.get("xml") or result.get("content")
                if not xml:
                    logger.error("No XML in draw.io response", response=result)
                    raise GenerationError("No XML content in draw.io response")

                # Validate XML structure
                if not xml.strip().startswith("<"):
                    logger.error("Invalid XML format from draw.io")
                    raise GenerationError("Response does not contain valid XML")

                logger.debug(f"Generated XML length: {len(xml)} chars")
                return xml

        except httpx.TimeoutException:
            logger.error("HTTP timeout calling draw.io service")
            raise GenerationError("Draw.io service request timed out")
        except httpx.ConnectError as e:
            logger.error(f"Failed to connect to draw.io service: {e}")
            raise GenerationError(
                f"Cannot connect to draw.io service at {self.drawio_url}"
            )
        except GenerationError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in diagram generation: {e}")
            raise GenerationError(f"Unexpected error: {str(e)}")
