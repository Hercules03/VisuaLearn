"""SVG Converter service for rendering diagrams to SVG format."""

from loguru import logger

from app.config import settings
from app.errors import RenderingError


class ImageConverter:
    """Service for converting draw.io XML diagrams to displayable format."""

    def __init__(self):
        """Initialize SVG converter with configuration."""
        self.drawio_url = settings.drawio_service_url
        self.timeout = settings.image_timeout
        logger.info(
            "Image converter initialized",
            drawio_url=self.drawio_url,
            timeout=self.timeout,
        )

    async def to_svg(self, xml: str) -> str:
        """Return draw.io XML for frontend rendering.

        The draw.io XML format is compatible with draw.io renderer libraries.
        The frontend uses this XML to render the diagram interactively.

        Args:
            xml: draw.io XML diagram content

        Returns:
            draw.io XML content (as svg_content)

        Raises:
            RenderingError: If XML is invalid
        """
        logger.info("Preparing diagram for display", xml_length=len(xml))

        try:
            if not xml or not xml.strip().startswith("<"):
                raise RenderingError("Invalid XML format for rendering")

            # Return the XML as-is. The frontend will render it using draw.io library.
            # This is the draw.io diagram XML format which the frontend can render directly.
            logger.info(
                "Diagram prepared for frontend rendering",
                xml_length=len(xml),
                has_cells=xml.count("<mxCell") > 0,
            )
            return xml

        except RenderingError:
            raise
        except Exception as e:
            logger.error(f"Diagram preparation failed: {e}")
            raise RenderingError(f"Failed to prepare diagram: {str(e)}")
