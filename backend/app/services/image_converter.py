"""SVG conversion service for draw.io diagrams.

Converts draw.io XML diagrams to SVG format for frontend rendering.

Architecture:
1. Backend: Receives XML from diagram generator
2. Validation: Validates XML structure using lxml
3. Conversion: Converts XML to SVG using Playwright (proper lifecycle)
4. Returns: SVG content for frontend rendering
5. Frontend: Renders SVG directly with react-svg or native <svg>

Resource Management:
- Shared browser instance (created once, reused across requests)
- Proper cleanup on app shutdown
- Connection pooling to prevent crashes
- Error recovery with automatic reconnection
"""

import asyncio
import base64
from lxml import etree

from loguru import logger
from playwright.async_api import async_playwright, Browser

from app.errors import RenderingError

# Global browser instance (singleton pattern)
_browser_instance: Browser | None = None


class ImageConverter:
    """Service for converting draw.io XML to SVG."""

    def __init__(self):
        """Initialize image converter."""
        self._browser = None
        logger.info("Image converter initialized")

    async def _get_browser(self) -> Browser:
        """Get or create the shared browser instance with proper lifecycle.

        Uses singleton pattern to reuse browser across requests.
        Handles reconnection if browser crashes.
        """
        global _browser_instance

        # Check if global browser exists and is still alive
        if _browser_instance is not None:
            try:
                # Simple health check: try to create a page
                page = await asyncio.wait_for(_browser_instance.new_page(), timeout=2.0)
                await page.close()
                return _browser_instance
            except Exception as e:
                logger.warning(f"Browser health check failed, reconnecting: {e}")
                _browser_instance = None

        # Create new browser instance
        try:
            logger.info("Initializing Playwright browser (singleton)")
            playwright = await async_playwright().start()
            _browser_instance = await playwright.chromium.launch(headless=True)
            logger.info("Playwright browser initialized successfully")
            return _browser_instance
        except Exception as e:
            logger.error(f"Failed to initialize browser: {e}", exc_info=True)
            raise RenderingError(f"Failed to initialize rendering engine: {str(e)}")

    async def validate_xml(self, xml: str) -> str:
        """Validate draw.io XML structure.

        Validates XML structure and returns it for frontend rendering.
        Frontend uses react-drawio component for client-side rendering.

        Args:
            xml: draw.io XML diagram content

        Returns:
            Validated draw.io XML

        Raises:
            RenderingError: If XML is invalid
        """
        logger.info("Validating diagram XML", xml_length=len(xml))

        try:
            # 1. Validate XML is not empty
            if not xml or not xml.strip():
                raise RenderingError("Empty XML provided")

            # 2. Parse and validate XML
            try:
                root = etree.fromstring(xml.encode("utf-8"))
            except etree.XMLSyntaxError as e:
                raise RenderingError(f"Invalid XML syntax: {str(e)}")

            # 3. Validate draw.io structure
            tag_name = root.tag.split("}")[-1] if "}" in root.tag else root.tag
            if tag_name != "mxfile":
                raise RenderingError(f"Expected <mxfile> root element, got <{tag_name}>")

            diagram = root.find("{*}diagram")
            if diagram is None:
                diagram = root.find("diagram")
            if diagram is None:
                raise RenderingError("Missing <diagram> element")

            model = diagram.find("{*}mxGraphModel")
            if model is None:
                model = diagram.find("mxGraphModel")
            if model is None:
                raise RenderingError("Missing <mxGraphModel> element")

            cells_root = model.find("{*}root")
            if cells_root is None:
                cells_root = model.find("root")
            if cells_root is None:
                raise RenderingError("Missing diagram cells (<root> element)")

            cells = cells_root.findall("{*}mxCell")
            if not cells:
                cells = cells_root.findall("mxCell")
            if len(cells) < 2:
                raise RenderingError(f"Diagram has insufficient cells: {len(cells)} (minimum 2)")

            logger.info("XML validation successful", cells=len(cells))
            return xml

        except RenderingError:
            raise
        except Exception as e:
            logger.error(f"XML validation failed: {e}", exc_info=True)
            raise RenderingError(f"Failed to validate diagram XML: {str(e)}")

    async def to_svg(self, xml: str) -> str:
        """Convert draw.io XML to SVG.

        Validates XML and converts to SVG using Playwright for accurate rendering.

        Args:
            xml: draw.io XML diagram content

        Returns:
            SVG content as string

        Raises:
            RenderingError: If XML is invalid or conversion fails
        """
        logger.info("Converting diagram to SVG", xml_length=len(xml))

        try:
            # 1. Validate XML first
            await self.validate_xml(xml)

            # 2. Get browser instance
            browser = await self._get_browser()

            # 3. Create HTML page with draw.io embedded
            html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Diagram Render</title>
    <script src="https://cdn.jsdelivr.net/npm/mxgraph@4.2.2/javascript/mxClient.min.js"></script>
    <style>
        body {{ margin: 0; padding: 0; }}
        #diagram {{ width: 100%; height: 100%; }}
    </style>
</head>
<body>
    <div id="diagram"></div>
    <script>
        // Decode and render the diagram
        var xml = decodeURIComponent('{self._encode_xml_for_js(xml)}');
        var container = document.getElementById('diagram');
        var graph = new mxGraph(container);
        var codec = new mxCodec();
        var node = mxUtils.parseXml(xml).documentElement;
        codec.decode(node, graph.getModel());
        graph.fit();

        // Auto-size the container
        var bounds = graph.getGraphBounds();
        container.style.width = Math.ceil(bounds.width + 40) + 'px';
        container.style.height = Math.ceil(bounds.height + 40) + 'px';

        // Export to SVG
        var svg = mxUtils.getPrettyXml(
            new mxXmlExport().exportNode(graph.getModel().getRoot())
        );
        window.svgContent = svg;
    </script>
</body>
</html>"""

            # 4. Render and capture SVG
            page = await asyncio.wait_for(browser.new_page(), timeout=5.0)
            try:
                await asyncio.wait_for(page.set_content(html_content), timeout=8.0)
                await asyncio.wait_for(asyncio.sleep(1), timeout=2.0)  # Wait for rendering

                # Get SVG from browser
                svg_content = await asyncio.wait_for(
                    page.evaluate("window.svgContent || ''"), timeout=3.0
                )

                if not svg_content:
                    logger.warning("SVG export from browser returned empty")
                    # Fallback: Try direct screenshot as SVG
                    svg_content = await self._screenshot_to_svg(page)

                logger.info("Diagram converted to SVG successfully", svg_length=len(svg_content))
                return svg_content

            finally:
                await asyncio.wait_for(page.close(), timeout=2.0)

        except asyncio.TimeoutError as e:
            logger.error(f"SVG conversion timed out: {e}")
            raise RenderingError(f"Diagram rendering timed out: {str(e)}")
        except RenderingError:
            raise
        except Exception as e:
            logger.error(f"SVG conversion failed: {e}", exc_info=True)
            raise RenderingError(f"Failed to convert diagram to SVG: {str(e)}")

    async def _screenshot_to_svg(self, page) -> str:
        """Fallback: Convert screenshot to SVG data URI.

        Args:
            page: Playwright page object

        Returns:
            SVG with embedded base64 PNG image

        Raises:
            RenderingError: If screenshot fails
        """
        try:
            screenshot_bytes = await asyncio.wait_for(
                page.screenshot(type="png"), timeout=4.0
            )
            png_base64 = base64.b64encode(screenshot_bytes).decode("utf-8")

            # Get screenshot dimensions
            viewport = page.viewport
            width = viewport.get("width", 1200) if viewport else 1200
            height = viewport.get("height", 800) if viewport else 800

            # Wrap in SVG
            svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">
    <image href="data:image/png;base64,{png_base64}" width="{width}" height="{height}"/>
</svg>"""

            logger.info("Fallback: Created SVG from screenshot")
            return svg
        except Exception as e:
            logger.error(f"Fallback SVG conversion failed: {e}")
            raise RenderingError(f"Failed to create diagram SVG: {str(e)}")

    @staticmethod
    def _encode_xml_for_js(xml: str) -> str:
        """Encode XML for safe inclusion in JavaScript string.

        Args:
            xml: XML content to encode

        Returns:
            URL-encoded and escaped XML
        """
        import urllib.parse

        # Escape for JavaScript string literal
        escaped = xml.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n")
        # URL encode for safe transmission
        return urllib.parse.quote(escaped)
