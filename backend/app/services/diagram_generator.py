"""Diagram Generator service for creating draw.io XML diagrams via next-ai-draw-io HTTP API."""

import asyncio
import json

import httpx
from loguru import logger

from app.config import settings
from app.errors import GenerationError
from app.services.planning_agent import PlanningOutput


class DiagramGenerator:
    """Service for generating draw.io XML diagrams via next-ai-draw-io.

    Pipeline:
    1. Convert PlanningOutput to natural language prompt
    2. POST to next-ai-draw-io /api/chat endpoint
    3. Get mxGraphModel XML draft
    4. Return XML (refinement happens in Orchestrator via MCP)
    """

    def __init__(self):
        """Initialize diagram generator with next-ai-draw-io service URL."""
        self.drawio_url = settings.drawio_service_url
        self.timeout = settings.generation_timeout
        logger.info(
            "Diagram generator initialized (HTTP to next-ai-draw-io)",
            drawio_url=self.drawio_url,
        )

    async def generate(self, plan: PlanningOutput) -> str:
        """Generate diagram XML draft from planning specifications.

        Converts PlanningOutput to a natural language prompt and sends it
        to next-ai-draw-io /api/chat endpoint for XML generation.

        Args:
            plan: PlanningOutput with diagram specifications

        Returns:
            draw.io XML string representing the diagram draft

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
            # Convert plan to natural language prompt
            prompt = self._create_diagram_prompt(plan)

            # Generate XML via HTTP call to next-ai-draw-io
            xml = await asyncio.wait_for(
                self._generate_xml_via_http(prompt),
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

    async def _generate_xml_via_http(self, prompt: str) -> str:
        """Generate mxGraphModel XML via next-ai-draw-io HTTP API.

        Args:
            prompt: Natural language description of the diagram to create

        Returns:
            mxGraphModel XML string

        Raises:
            GenerationError: If HTTP request fails or response is invalid
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Send prompt to next-ai-draw-io /api/chat endpoint
                # Messages must be in Vercel AI SDK UIMessage format with 'parts' array
                payload = {
                    "messages": [
                        {
                            "role": "user",
                            "parts": [
                                {
                                    "type": "text",
                                    "text": prompt
                                }
                            ]
                        }
                    ]
                }
                
                response = await client.post(
                    f"{self.drawio_url}/api/chat",
                    json=payload,
                    headers={"Content-Type": "application/json"},
                )

                if response.status_code != 200:
                    error_text = response.text[:500] if response.text else "(no response body)"
                    logger.error(
                        f"next-ai-draw-io API error: {response.status_code}",
                        response_text=error_text,
                    )
                    raise GenerationError(
                        f"Diagram generation service failed ({response.status_code}). Please check your configuration and try again."
                    )

                # The response is a Vercel AI SDK stream (Data Stream Protocol)
                # We need to extract the XML from the display_diagram tool call or raw text
                response_text = response.text

                if not response_text or response_text.strip() == "":
                    logger.error(
                        "Empty response from next-ai-draw-io",
                    )
                    raise GenerationError(
                        "Diagram generation service returned empty response"
                    )

                import re

                # Debug: Log response for troubleshooting
                logger.debug(f"next-ai-draw-io response length: {len(response_text)}")
                if len(response_text) < 500:
                    logger.debug(f"Full response: {response_text}")
                else:
                    logger.debug(f"Response start: {response_text[:500]}")

                xml = None

                # Method 1: Try to parse Vercel AI SDK Data Stream Protocol format
                # Lines contain data: {json} format
                try:
                    lines = response_text.strip().split('\n')
                    for line in lines:
                        if line.startswith('d:'):
                            try:
                                # Parse data stream line
                                json_str = line[2:]  # Remove "d:" prefix
                                data = json.loads(json_str)

                                # Check for tool-input with XML
                                if data.get('type') == 'tool-input-available':
                                    input_data = data.get('input', {})
                                    if 'xml' in input_data:
                                        xml = input_data['xml']
                                        logger.debug("XML extracted from data stream tool-input")
                                        break
                            except json.JSONDecodeError:
                                pass  # Continue to next line
                except Exception as e:
                    logger.debug(f"Data stream parsing failed: {e}")

                # Method 2: Look for JSON-escaped "xml" field in tool calls
                if not xml:
                    try:
                        # Pattern: "xml":"<mxGraphModel..." - more flexible pattern
                        xml_match = re.search(
                            r'"xml"\s*:\s*"((?:\\.|[^"\\])*)"',
                            response_text,
                            re.DOTALL
                        )
                        if xml_match:
                            xml_escaped = xml_match.group(1)
                            try:
                                # Properly unescape JSON string
                                xml = json.loads(f'"{xml_escaped}"')
                                logger.debug("XML extracted via JSON field pattern")
                            except json.JSONDecodeError:
                                # Manual unescape
                                xml = xml_escaped.replace('\\"', '"').replace('\\/', '/').replace('\\n', '\n').replace('\\t', '\t')
                                logger.debug("XML extracted via manual unescape")
                    except Exception as e:
                        logger.debug(f"JSON field extraction failed: {e}")

                # Method 3: Look for complete XML structures
                if not xml:
                    try:
                        # Try mxfile first (complete wrapper)
                        match = re.search(r'(<mxfile[^>]*>.*?</mxfile>)', response_text, re.DOTALL)
                        if match:
                            xml = match.group(1)
                            logger.debug("XML extracted via mxfile pattern")
                    except Exception as e:
                        logger.debug(f"mxfile pattern extraction failed: {e}")

                # Method 4: Look for mxGraphModel
                if not xml:
                    try:
                        match = re.search(r'(<mxGraphModel[^>]*>.*?</mxGraphModel>)', response_text, re.DOTALL)
                        if match:
                            xml = match.group(1)
                            logger.debug("XML extracted via mxGraphModel pattern")
                    except Exception as e:
                        logger.debug(f"mxGraphModel pattern extraction failed: {e}")

                # Method 5: Look for root tag with cells
                if not xml:
                    try:
                        match = re.search(r'(<root[^>]*>.*?</root>)', response_text, re.DOTALL)
                        if match:
                            xml = match.group(1)
                            logger.debug("XML extracted via root pattern")
                    except Exception as e:
                        logger.debug(f"root pattern extraction failed: {e}")

                # Method 6: Extract all mxCell elements as a group
                if not xml:
                    try:
                        match = re.search(r'(<mxCell[^>]*>.*?</mxCell>(?:\s*<mxCell[^>]*>.*?</mxCell>)*)', response_text, re.DOTALL)
                        if match:
                            xml = match.group(1)
                            logger.debug("XML extracted via mxCell group pattern")
                    except Exception as e:
                        logger.debug(f"mxCell group extraction failed: {e}")

                # Method 7: Last resort - find first <mx and get everything until > or closing tag
                if not xml:
                    try:
                        # Look for any tag that starts with <mx
                        start_match = re.search(r'<mx\w+', response_text)
                        if start_match:
                            start_pos = start_match.start()
                            # Try to find balanced closing tags
                            xml_attempt = response_text[start_pos:]

                            # Find the corresponding closing tag
                            tag_name = xml_attempt.split('>')[0].split()[0][1:]  # Extract tag name
                            closing_tag = f'</{tag_name}>'

                            close_pos = xml_attempt.rfind(closing_tag)
                            if close_pos != -1:
                                xml = xml_attempt[:close_pos + len(closing_tag)]
                                logger.debug(f"XML extracted via fallback tag matching ({tag_name})")
                    except Exception as e:
                        logger.debug(f"Fallback tag extraction failed: {e}")

                if not xml:
                    logger.error(
                        "No XML found in response from next-ai-draw-io",
                        response_length=len(response_text),
                        response_preview=response_text[:300],
                    )
                    raise GenerationError(
                        "Diagram generation service did not return valid diagram XML"
                    )

                # Handle case where XML might be wrapped in markdown code blocks
                if isinstance(xml, str):
                    if "```xml" in xml:
                        xml = xml.split("```xml")[1].split("```")[0].strip()
                    elif "```" in xml:
                        try:
                            xml = xml.split("```")[1].split("```")[0].strip()
                        except IndexError:
                            pass  # Keep original if split fails

                # Validate XML structure
                mxcell_count = xml.count("<mxCell")
                logger.debug(f"Extracted XML has {mxcell_count} mxCell elements")

                # If we have very few cells, the extraction might have failed
                if mxcell_count < 2:
                    logger.warning(
                        f"XML appears incomplete: only {mxcell_count} cells extracted",
                        xml_preview=xml[:200],
                    )
                    logger.debug(f"Full extracted XML: {xml}")

                if "<mxCell" not in xml and "<mxfile" not in xml and "<mxGraphModel" not in xml:
                    logger.error(
                        "Generated content does not contain any diagram elements",
                        xml_start=xml[:100],
                    )
                    raise GenerationError(
                        "Generated content does not contain valid diagram elements"
                    )

                # If XML is just bare mxCell elements, wrap them in proper structure
                if not (xml.strip().startswith("<mxfile") or xml.strip().startswith("<mxGraphModel") or xml.strip().startswith("<root")):
                    if "<mxCell" in xml:
                        # It's bare cells, wrap them
                        logger.debug("Wrapping bare mxCell elements in proper structure")
                        xml = f"""<mxfile host="app.diagrams.net" modified="2025-01-28T00:00:00.000Z" agent="VisuaLearn" version="1.0" type="device">
  <diagram id="default" name="Default">
    <mxGraphModel dx="0" dy="0" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1200" pageHeight="800" math="0" shadow="0">
      <root>
        <mxCell id="0" value="" parent="" vertex="1" />
        <mxCell id="1" value="" parent="0" vertex="1" />
        {xml}
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>"""
                        logger.debug("XML wrapped successfully")

                logger.debug("XML generated by next-ai-draw-io", xml_length=len(xml))
                return xml

        except asyncio.TimeoutError:
            logger.error(f"next-ai-draw-io request timed out after {self.timeout}s")
            raise GenerationError(
                f"Diagram generation timed out after {self.timeout}s"
            )
        except httpx.RequestError as e:
            logger.error(f"HTTP request to next-ai-draw-io failed: {e}")
            raise GenerationError(
                f"Failed to connect to next-ai-draw-io service: {str(e)}"
            )
        except Exception as e:
            logger.error(f"XML generation failed: {e}", exc_info=True)
            raise GenerationError(f"Failed to generate XML: {str(e)}")

    def _create_diagram_prompt(self, plan: PlanningOutput) -> str:
        """Create a natural language prompt for diagram generation.

        Args:
            plan: PlanningOutput with diagram specifications

        Returns:
            Prompt string for next-ai-draw-io to generate diagram XML
        """
        components_str = "\n".join(f"  - {c}" for c in plan.components)
        relationships_str = "\n".join(
            f"  - {r['from']} → {r['to']}: {r.get('label', '')}"
            for r in plan.relationships
        )
        insights_str = "\n".join(f"  - {i}" for i in plan.key_insights)
        criteria_str = "\n".join(f"  - {c}" for c in plan.success_criteria)

        prompt = f"""Create a {plan.diagram_type} diagram for educational purposes about: {plan.concept}

**Components to include (ALL required - {len(plan.components)} total):**
{components_str}

**Relationships to show (ALL required - {len(plan.relationships)} total):**
{relationships_str}

**Key Teaching Points:**
{insights_str}

**Success Criteria:**
{criteria_str}

**Requirements:**
1. Create a complete {plan.diagram_type} diagram
2. Include ALL {len(plan.components)} components listed above
3. Show ALL {len(plan.relationships)} relationships between components
4. Use clear, readable labels for all elements
5. Apply appropriate shapes and colors for visual clarity and {plan.diagram_type} standards
6. Use realistic positioning (0-800 x, 0-600 y coordinates)
7. Ensure connections don't overlap by using different exit/entry points
8. Make it age-appropriate and pedagogically sound
9. Return the complete, valid draw.io XML diagram

Generate the diagram XML now."""

        return prompt
