"""Image conversion service for draw.io diagrams.

Converts draw.io XML diagrams for frontend display.
Returns XML that will be rendered by the frontend (demo mode) or processed further.

Architecture:
1. Backend: Receives XML from diagram generator
2. Validation: Validates XML structure
3. Return: Returns XML string for display
4. Frontend: Renders using available rendering engine
"""

from lxml import etree

from loguru import logger

from app.errors import RenderingError


class ImageConverter:
    """Service for validating and preparing draw.io XML diagrams."""

    def __init__(self):
        """Initialize image converter."""
        logger.info("Image converter initialized")

    async def to_svg(self, xml: str) -> str:
        """Validate draw.io XML and return for frontend rendering.

        For now, returns XML as-is (frontend will handle rendering).
        In production, this would render to SVG/PNG via Playwright or similar.

        Args:
            xml: draw.io XML diagram content

        Returns:
            XML content string for frontend rendering

        Raises:
            RenderingError: If XML is invalid
        """
        logger.info("Validating diagram XML", xml_length=len(xml))

        try:
            # 1. Validate XML structure
            if not xml or not xml.strip():
                raise RenderingError("Empty XML provided")

            # 2. Parse XML to validate syntax
            try:
                root = etree.fromstring(xml.encode("utf-8"))
            except etree.XMLSyntaxError as e:
                raise RenderingError(f"Invalid XML syntax: {str(e)}")

            # 3. Validate draw.io structure
            # Check root element is <mxfile> (handle namespaces)
            tag_name = root.tag.split("}")[-1] if "}" in root.tag else root.tag
            if tag_name != "mxfile":
                raise RenderingError(f"Expected <mxfile> root element, got <{tag_name}>")

            # Check for required <diagram> element (use wildcard for namespace)
            diagram = root.find("{*}diagram")
            if diagram is None:
                diagram = root.find("diagram")
            if diagram is None:
                raise RenderingError("Missing <diagram> element in draw.io XML")

            # Check for required <mxGraphModel> element (use wildcard for namespace)
            model = diagram.find("{*}mxGraphModel")
            if model is None:
                model = diagram.find("mxGraphModel")
            if model is None:
                raise RenderingError("Missing <mxGraphModel> element in diagram")

            # Check for <root> cell container (use wildcard for namespace)
            cells_root = model.find("{*}root")
            if cells_root is None:
                cells_root = model.find("root")
            if cells_root is None:
                raise RenderingError("Missing diagram cells (<root> element not found)")

            # Count cells in the diagram (handle namespaces)
            cells = cells_root.findall("{*}mxCell")
            if not cells:
                cells = cells_root.findall("mxCell")
            cell_count = len(cells)
            if cell_count < 2:
                raise RenderingError(
                    f"Diagram has insufficient cells: {cell_count} (minimum 2 required)"
                )

            logger.info(
                "XML structure validated",
                cells=cell_count,
                vertices=[c for c in cells if c.get("vertex") == "1"],
                edges=[c for c in cells if c.get("edge") == "1"],
            )

            # For demo: return XML as-is
            # In production: would render to SVG via Playwright or draw.io API
            return xml

        except RenderingError:
            raise
        except Exception as e:
            logger.error(f"XML validation failed: {e}", exc_info=True)
            raise RenderingError(f"Failed to validate diagram: {str(e)}")
