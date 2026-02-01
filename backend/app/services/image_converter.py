"""Image conversion service for draw.io diagrams.

Converts draw.io XML diagrams to PNG format for frontend display.

Architecture:
1. Backend: Receives XML from diagram generator
2. Validation: Validates XML structure using lxml
3. Rendering: Converts XML to PNG using Playwright + draw.io
4. Encoding: Returns base64-encoded PNG for frontend display
5. Frontend: Displays PNG image directly (no CSP issues)
"""

import base64
import asyncio
from lxml import etree

from loguru import logger
from playwright.async_api import async_playwright

from app.errors import RenderingError


class ImageConverter:
    """Service for converting draw.io XML diagrams to PNG format."""

    def __init__(self):
        """Initialize image converter."""
        self._playwright = None
        self._browser = None
        logger.info("Image converter initialized")

    async def _ensure_browser(self):
        """Ensure Playwright browser is initialized."""
        if self._browser is None:
            try:
                if self._playwright is None:
                    self._playwright = await async_playwright().start()
                self._browser = await self._playwright.chromium.launch()
                logger.info("Playwright browser initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Playwright: {e}")
                raise RenderingError(f"Failed to initialize rendering engine: {str(e)}")

    async def to_svg(self, xml: str) -> str:
        """Render draw.io XML to base64-encoded PNG.

        Validates XML structure, then uses Playwright to render to PNG via
        the draw.io rendering engine embedded in an HTML page.

        Args:
            xml: draw.io XML diagram content

        Returns:
            Base64-encoded PNG image as data URL for frontend display

        Raises:
            RenderingError: If XML is invalid or rendering fails
        """
        logger.info("Converting diagram to PNG", xml_length=len(xml))

        try:
            # 1. Validate XML structure
            if not xml or not xml.strip():
                raise RenderingError("Empty XML provided")

            # 2. Parse and validate XML
            try:
                root = etree.fromstring(xml.encode("utf-8"))
            except etree.XMLSyntaxError as e:
                raise RenderingError(f"Invalid XML syntax: {str(e)}")

            # Validate draw.io structure
            tag_name = root.tag.split("}")[-1] if "}" in root.tag else root.tag
            if tag_name != "mxfile":
                raise RenderingError(f"Expected <mxfile> root element, got <{tag_name}>")

            diagram = root.find("{*}diagram") or root.find("diagram")
            if diagram is None:
                raise RenderingError("Missing <diagram> element")

            model = diagram.find("{*}mxGraphModel") or diagram.find("mxGraphModel")
            if model is None:
                raise RenderingError("Missing <mxGraphModel> element")

            cells_root = model.find("{*}root") or model.find("root")
            if cells_root is None:
                raise RenderingError("Missing diagram cells (<root> element)")

            cells = cells_root.findall("{*}mxCell") or cells_root.findall("mxCell")
            if len(cells) < 2:
                raise RenderingError(f"Diagram has insufficient cells: {len(cells)} (minimum 2)")

            logger.info("XML structure validated", cells=len(cells))

            # 3. Render XML to PNG using Playwright
            await self._ensure_browser()

            # Create HTML page that renders the diagram
            html = f"""<!DOCTYPE html>
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

        // Adjust canvas size to fit content
        var bounds = graph.getGraphBounds();
        container.style.width = Math.ceil(bounds.width + 20) + 'px';
        container.style.height = Math.ceil(bounds.height + 20) + 'px';
    </script>
</body>
</html>"""

            page = await self._browser.new_page()
            try:
                await page.set_content(html)
                await asyncio.sleep(2)  # Wait for rendering

                # Take screenshot
                screenshot = await page.screenshot(type="png")
                base64_png = base64.b64encode(screenshot).decode("utf-8")

                logger.info("Diagram rendered to PNG", size_bytes=len(screenshot))
                return f"data:image/png;base64,{base64_png}"

            finally:
                await page.close()

        except RenderingError:
            raise
        except Exception as e:
            logger.error(f"Rendering failed: {e}", exc_info=True)
            raise RenderingError(f"Failed to render diagram: {str(e)}")

    @staticmethod
    def _encode_xml_for_js(xml: str) -> str:
        """Encode XML for safe inclusion in JavaScript string."""
        # Replace special characters for JavaScript string literal
        encoded = xml.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n")
        # URL encode for safe transmission
        import urllib.parse
        return urllib.parse.quote(encoded)
