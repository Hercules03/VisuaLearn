"""Image Converter service for rendering diagrams to PNG/SVG."""

import asyncio
import json

from loguru import logger
from playwright.async_api import async_playwright

from app.config import settings
from app.errors import RenderingError


class ImageConverter:
    """Service for converting draw.io XML diagrams to PNG and SVG images."""

    def __init__(self):
        """Initialize image converter with configuration."""
        self.timeout = settings.image_timeout
        self.drawio_url = settings.drawio_service_url
        logger.info(
            "Image converter initialized",
            drawio_url=self.drawio_url,
            timeout=self.timeout,
        )

    async def to_png(self, xml: str) -> bytes:
        """Convert diagram XML to PNG image bytes.

        Renders the draw.io XML diagram to a PNG image using Playwright.

        Args:
            xml: draw.io XML diagram content

        Returns:
            PNG image as bytes

        Raises:
            RenderingError: If conversion fails or timeout occurs
        """
        logger.info("PNG conversion started", xml_length=len(xml))

        try:
            # Run conversion with timeout
            png_bytes = await asyncio.wait_for(
                self._to_png_internal(xml),
                timeout=self.timeout,
            )
            logger.info("PNG conversion completed", size_bytes=len(png_bytes))
            return png_bytes
        except asyncio.TimeoutError:
            logger.error(f"PNG conversion timed out after {self.timeout}s")
            raise RenderingError(f"PNG rendering timed out after {self.timeout}s.")
        except RenderingError:
            # Re-raise RenderingErrors as-is
            raise
        except Exception as e:
            logger.error(f"PNG conversion failed: {e}")
            raise RenderingError(f"Failed to convert to PNG: {str(e)}")

    async def to_svg(self, xml: str) -> str:
        """Convert diagram XML to SVG string.

        Renders the draw.io XML diagram to an SVG format.

        Args:
            xml: draw.io XML diagram content

        Returns:
            SVG content as string

        Raises:
            RenderingError: If conversion fails or timeout occurs
        """
        logger.info("SVG conversion started", xml_length=len(xml))

        try:
            # Run conversion with timeout
            svg_str = await asyncio.wait_for(
                self._to_svg_internal(xml),
                timeout=self.timeout,
            )
            logger.info("SVG conversion completed", size_chars=len(svg_str))
            return svg_str
        except asyncio.TimeoutError:
            logger.error(f"SVG conversion timed out after {self.timeout}s")
            raise RenderingError(f"SVG rendering timed out after {self.timeout}s.")
        except RenderingError:
            # Re-raise RenderingErrors as-is
            raise
        except Exception as e:
            logger.error(f"SVG conversion failed: {e}")
            raise RenderingError(f"Failed to convert to SVG: {str(e)}")

    async def _to_png_internal(self, xml: str) -> bytes:
        """Internal PNG conversion using draw.io service.

        Args:
            xml: draw.io XML diagram content

        Returns:
            PNG image as bytes

        Raises:
            RenderingError: If rendering fails
        """
        if not xml or not xml.strip().startswith("<"):
            raise RenderingError("Invalid XML format for rendering")

        try:
            async with async_playwright() as p:
                # Launch browser (Chromium)
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context()
                page = await context.new_page()

                # Create HTML with embedded diagram
                html = self._create_html_from_xml(xml)

                # Navigate to HTML content
                await page.set_content(html)

                # Wait for diagram to render
                await page.wait_for_timeout(500)

                # Take screenshot
                png_bytes = await page.screenshot(full_page=False)

                # Cleanup
                await page.close()
                await context.close()
                await browser.close()

                if not png_bytes:
                    raise RenderingError("Screenshot generated empty PNG")

                return png_bytes

        except RenderingError:
            raise
        except Exception as e:
            logger.error(f"Playwright PNG rendering failed: {e}")
            raise RenderingError(f"Playwright rendering error: {str(e)}")

    async def _to_svg_internal(self, xml: str) -> str:
        """Internal SVG conversion using draw.io service.

        Args:
            xml: draw.io XML diagram content

        Returns:
            SVG content as string

        Raises:
            RenderingError: If rendering fails
        """
        if not xml or not xml.strip().startswith("<"):
            raise RenderingError("Invalid XML format for rendering")

        try:
            # Extract SVG from mxfile XML using draw.io conversion
            # For now, we'll convert via the draw.io service endpoint
            import httpx

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.drawio_url}/api/export",
                    json={"xml": xml, "format": "svg"},
                )

                if response.status_code != 200:
                    logger.error(f"Draw.io SVG export error: {response.status_code}")
                    raise RenderingError(
                        f"Draw.io service returned {response.status_code}"
                    )

                try:
                    result = response.json()
                except json.JSONDecodeError:
                    # If response is raw SVG, use it directly
                    if response.text.startswith("<svg"):
                        return response.text
                    raise RenderingError("Invalid SVG response format")

                svg = result.get("svg") or result.get("content")
                if not svg:
                    logger.error("No SVG in draw.io response", response=result)
                    raise RenderingError("No SVG content in response")

                if not svg.strip().startswith("<svg"):
                    raise RenderingError("Response does not contain valid SVG")

                return svg

        except httpx.ConnectError as e:
            logger.error(f"Failed to connect to draw.io service: {e}")
            raise RenderingError(
                f"Cannot connect to draw.io service at {self.drawio_url}"
            )
        except httpx.TimeoutException:
            logger.error("HTTP timeout calling draw.io service")
            raise RenderingError("Draw.io service request timed out")
        except RenderingError:
            raise
        except Exception as e:
            logger.error(f"SVG conversion failed: {e}")
            raise RenderingError(f"Unexpected error: {str(e)}")

    def _create_html_from_xml(self, xml: str) -> str:
        """Create HTML document containing the diagram for rendering.

        Args:
            xml: draw.io XML diagram content

        Returns:
            HTML string with embedded diagram

        Raises:
            RenderingError: If XML is invalid
        """
        if not xml:
            raise RenderingError("Cannot create HTML from empty XML")

        # Escape XML for embedding in HTML
        escaped_xml = xml.replace("&", "&amp;").replace('"', "&quot;")

        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ margin: 0; padding: 10px; }}
        svg {{ display: block; }}
    </style>
</head>
<body>
    <div id="diagram"></div>
    <script src="https://cdn.jsdelivr.net/npm/mxgraph@4.1.0/javascript/mxClient.min.js"></script>
    <script>
        mxgraph.mxCodecRegistry.register(
            new mxgraph.mxObjectCodec(
                new mxgraph.mxGraphModel(),
                ["cells"]
            )
        );

        var container = document.getElementById("diagram");
        var graph = new mxgraph.mxGraph(container);
        var codec = new mxgraph.mxCodec();
        var node = mxgraph.mxUtils.parseXml("{escaped_xml}").documentElement;
        codec.decode(node, graph.getModel());
        graph.fit();
    </script>
</body>
</html>"""

        return html
