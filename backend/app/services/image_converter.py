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

        browser = None
        context = None
        page = None

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

                if not png_bytes:
                    raise RenderingError("Screenshot generated empty PNG")

                return png_bytes

        except RenderingError:
            raise
        except Exception as e:
            logger.error(f"Playwright PNG rendering failed: {e}")
            raise RenderingError(f"Playwright rendering error: {str(e)}")
        finally:
            # Ensure cleanup happens even if errors occur
            try:
                if page:
                    await page.close()
                if context:
                    await context.close()
                if browser:
                    await browser.close()
            except Exception as e:
                logger.warning(f"Error during browser cleanup: {e}")

    async def _to_svg_internal(self, xml: str) -> str:
        """Internal SVG conversion using draw.io service or fallback.

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
            # Try to extract SVG from mxfile XML using draw.io conversion
            import httpx

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Try primary endpoint
                response = await client.post(
                    f"{self.drawio_url}/api/export",
                    json={"xml": xml, "format": "svg"},
                )

                if response.status_code == 404:
                    # Fallback: try alternative endpoint
                    logger.warning(
                        "SVG export endpoint not found, trying alternative"
                    )
                    response = await client.post(
                        f"{self.drawio_url}/api/export",
                        data=xml,
                        headers={"Content-Type": "application/xml"},
                        params={"format": "svg"},
                    )

                if response.status_code != 200:
                    logger.warning(
                        f"Draw.io SVG export service unavailable ({response.status_code}), using fallback SVG",
                        status_code=response.status_code,
                    )
                    # Fallback: generate minimal SVG from XML
                    return self._generate_fallback_svg(xml)

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

    def _generate_fallback_svg(self, xml: str) -> str:
        """Generate a minimal SVG as fallback when draw.io service is unavailable.

        Args:
            xml: draw.io XML diagram content

        Returns:
            Basic SVG representation

        Raises:
            RenderingError: If XML is invalid
        """
        logger.info("Generating fallback SVG from XML")
        try:
            # Create a simple SVG that represents the diagram
            # This is a minimal fallback - just create a blank SVG with a message
            svg = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="800" height="600" viewBox="0 0 800 600">
    <defs>
        <style type="text/css"><![CDATA[
            text { font-family: Arial, sans-serif; font-size: 14px; }
            rect { fill: #ffffff; stroke: #999999; stroke-width: 1px; }
            .label { fill: #000000; }
            .note { fill: #ffffcc; stroke: #cccccc; stroke-width: 1px; }
        ]]></style>
    </defs>
    <rect class="note" x="50" y="50" width="700" height="500" rx="5" ry="5"/>
    <text class="label" x="75" y="200" font-size="16" font-weight="bold">Diagram Generated</text>
    <text class="label" x="75" y="230">This is a fallback representation.</text>
    <text class="label" x="75" y="260">The draw.io service may be unavailable.</text>
    <text class="label" x="75" y="290">Please check the PNG export or XML content.</text>
</svg>"""
            return svg
        except Exception as e:
            logger.error(f"Failed to generate fallback SVG: {e}")
            raise RenderingError(f"Failed to generate SVG: {str(e)}")
