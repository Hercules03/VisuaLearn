"""SVG conversion service for draw.io diagrams.

Converts draw.io XML diagrams to SVG format for frontend rendering.

Architecture:
1. Backend: Receives XML from diagram generator
2. Validation: Validates XML structure using lxml
3. Export: Uses draw.io Desktop CLI to export XML to SVG
4. Returns: SVG file for frontend rendering and download

This approach uses the official draw.io CLI, which:
- Works reliably on macOS (no Playwright/Chromium crashes)
- Produces pixel-perfect SVG matching draw.io rendering
- Supports all draw.io features and styles
"""

import asyncio
import tempfile
import subprocess
from pathlib import Path

from lxml import etree

from loguru import logger

from app.errors import RenderingError

# Path to draw.io CLI executable (can be customized via env)
DRAWIO_CLI = "/Applications/draw.io.app/Contents/MacOS/draw.io"

class ImageConverter:
    """Service for converting draw.io XML to SVG."""

    def __init__(self):
        """Initialize image converter."""
        logger.info("Image converter initialized")

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
        """Convert draw.io XML to SVG using draw.io CLI.

        Uses the official draw.io Desktop CLI to export XML to SVG.
        This approach:
        - Works reliably on macOS (no Playwright crashes)
        - Produces pixel-perfect SVG matching draw.io rendering
        - Supports all draw.io features and styles

        Args:
            xml: draw.io XML diagram content

        Returns:
            SVG content as string

        Raises:
            RenderingError: If XML is invalid or export fails
        """
        logger.info("Converting diagram to SVG using draw.io CLI", xml_length=len(xml))

        temp_input = None
        temp_output = None

        try:
            # 1. Validate XML first
            await self.validate_xml(xml)

            # 2. Convert dark mode colors to light mode for frontend display
            xml = self._convert_to_light_mode(xml)

            # 3. Create temporary files for draw.io CLI
            temp_input = tempfile.NamedTemporaryFile(
                mode='w', suffix='.drawio', delete=False, encoding='utf-8'
            )
            temp_input.write(xml)
            temp_input.close()

            temp_output = tempfile.NamedTemporaryFile(
                mode='r', suffix='.svg', delete=False, encoding='utf-8'
            )
            temp_output.close()

            input_path = temp_input.name
            output_path = temp_output.name

            logger.debug(
                "Created temp files for draw.io conversion",
                input_file=input_path,
                output_file=output_path,
            )

            # 4. Call draw.io CLI to export XML to SVG
            try:
                logger.info("Calling draw.io CLI for SVG export")
                result = await asyncio.wait_for(
                    asyncio.create_task(
                        self._run_drawio_export(input_path, output_path)
                    ),
                    timeout=30.0,  # 30 second timeout
                )

                if result is False:
                    raise RenderingError("draw.io CLI export failed (non-zero exit code)")

            except asyncio.TimeoutError:
                logger.error("draw.io CLI export timed out after 30 seconds")
                raise RenderingError("Diagram rendering timed out (exceeded 30s)")
            except FileNotFoundError:
                logger.error(
                    f"draw.io CLI not found at {DRAWIO_CLI}. "
                    "Install with: brew install --cask drawio"
                )
                raise RenderingError(
                    "Diagram rendering engine not available. "
                    "Please install draw.io Desktop."
                )
            except Exception as e:
                logger.error(f"draw.io CLI export failed: {e}")
                raise RenderingError(f"Failed to export diagram to SVG: {str(e)}")

            # 5. Read and return the generated SVG
            with open(output_path, 'r', encoding='utf-8') as f:
                svg_content = f.read()

            if not svg_content.strip():
                raise RenderingError("draw.io generated empty SVG file")

            logger.info(
                "Diagram converted to SVG successfully",
                svg_length=len(svg_content),
            )
            return svg_content

        except RenderingError:
            raise
        except Exception as e:
            logger.error(f"SVG conversion failed: {e}", exc_info=True)
            raise RenderingError(f"Failed to convert diagram to SVG: {str(e)}")

        finally:
            # Clean up temporary files
            if temp_input and Path(temp_input.name).exists():
                try:
                    Path(temp_input.name).unlink()
                    logger.debug("Cleaned up input temp file")
                except Exception as e:
                    logger.warning(f"Failed to clean up input temp file: {e}")

            if temp_output and Path(temp_output.name).exists():
                try:
                    Path(temp_output.name).unlink()
                    logger.debug("Cleaned up output temp file")
                except Exception as e:
                    logger.warning(f"Failed to clean up output temp file: {e}")

    @staticmethod
    def _convert_to_light_mode(xml: str) -> str:
        """Convert dark mode diagram colors to light mode for frontend display.

        Maps draw.io dark colors to light mode equivalents:
        - Dark Navy (#001a33, #0d1b2a, #1a2332) → Light Blue (#e3f2fd)
        - Dark Gray (#2c3e50) → Light Gray (#eceff1)
        - Dark text on light bg → Light text colors
        - Black connectors (#000000) → Dark Gray (#424242)

        Args:
            xml: draw.io XML with potentially dark colors

        Returns:
            XML with light mode colors
        """
        # Color mapping: dark mode → light mode
        color_map = {
            # Dark navy blues → light blue
            '#001a33': '#e3f2fd',
            '#0d1b2a': '#e3f2fd',
            '#1a2332': '#e3f2fd',
            '#1b3a52': '#e3f2fd',
            '#253a48': '#e3f2fd',
            '#2c3e50': '#eceff1',
            '#34495e': '#eceff1',
            '#2f3e4f': '#eceff1',

            # Dark browns/maroons → light browns
            '#5c4033': '#d7ccc8',
            '#6d4c41': '#d7ccc8',
            '#8d6e63': '#d7ccc8',
            '#795548': '#d7ccc8',

            # Black text → dark gray (for readability)
            '#000000': '#424242',

            # Very dark grays → medium gray
            '#1a1a1a': '#616161',
            '#262626': '#616161',
            '#333333': '#616161',
        }

        # Replace colors (case-insensitive to handle variations)
        result = xml
        for dark_color, light_color in color_map.items():
            # Replace exact matches (uppercase and lowercase)
            result = result.replace(dark_color, light_color)
            result = result.replace(dark_color.upper(), light_color)
            result = result.replace(dark_color.lower(), light_color)

        # Ensure background is white/light
        # Replace dark backgrounds in mxGraphModel
        if 'background="ffffff"' not in result:
            result = result.replace('background="000000"', 'background="ffffff"')
            result = result.replace('background="1a1a1a"', 'background="ffffff"')
            result = result.replace('background="2a2a2a"', 'background="ffffff"')

        logger.debug("Converted diagram to light mode colors")
        return result

    @staticmethod
    async def _run_drawio_export(input_file: str, output_file: str) -> bool:
        """Run draw.io CLI export command.

        Args:
            input_file: Path to input .drawio file
            output_file: Path to output .svg file

        Returns:
            True if successful, False otherwise
        """
        loop = asyncio.get_event_loop()

        def run_export():
            """Run draw.io export in executor (blocking operation)."""
            try:
                result = subprocess.run(
                    [
                        DRAWIO_CLI,
                        "-x",  # export mode
                        "-f", "svg",  # format: SVG
                        "-o", output_file,  # output file
                        input_file,  # input file
                    ],
                    capture_output=True,
                    text=True,
                    check=False,  # Don't raise on non-zero exit
                )

                if result.returncode != 0:
                    logger.error(
                        "draw.io export failed",
                        return_code=result.returncode,
                        stderr=result.stderr,
                        stdout=result.stdout,
                    )
                    return False

                logger.debug("draw.io export succeeded")
                return True

            except Exception as e:
                logger.error(f"Error running draw.io export: {e}")
                raise

        # Run in executor to avoid blocking
        return await loop.run_in_executor(None, run_export)


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
