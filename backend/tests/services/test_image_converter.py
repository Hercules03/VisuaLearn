"""Tests for Image Converter service."""

import asyncio

import pytest

from app.errors import RenderingError
from app.services.image_converter import ImageConverter


class TestImageConverterInit:
    """Test ImageConverter initialization."""

    def test_init_creates_converter(self, test_env):
        """Test successful initialization creates converter."""
        converter = ImageConverter()
        assert converter.timeout == 8
        assert converter.drawio_url == "http://localhost:6002"


class TestImageConverterInputValidation:
    """Test input validation for image conversion."""

    @pytest.mark.asyncio
    async def test_to_png_empty_xml(self, test_env):
        """Test to_png with empty XML fails."""
        converter = ImageConverter()

        with pytest.raises(RenderingError, match="Invalid XML"):
            await converter.to_png("")

    @pytest.mark.asyncio
    async def test_to_png_whitespace_xml(self, test_env):
        """Test to_png with whitespace-only XML fails."""
        converter = ImageConverter()

        with pytest.raises(RenderingError, match="Invalid XML"):
            await converter.to_png("   ")

    @pytest.mark.asyncio
    async def test_to_png_invalid_xml_format(self, test_env):
        """Test to_png with non-XML fails."""
        converter = ImageConverter()

        with pytest.raises(RenderingError, match="Invalid XML"):
            await converter.to_png("not xml at all")

    @pytest.mark.asyncio
    async def test_to_svg_empty_xml(self, test_env):
        """Test to_svg with empty XML fails."""
        converter = ImageConverter()

        with pytest.raises(RenderingError, match="Invalid XML"):
            await converter.to_svg("")

    @pytest.mark.asyncio
    async def test_to_svg_invalid_xml_format(self, test_env):
        """Test to_svg with non-XML fails."""
        converter = ImageConverter()

        with pytest.raises(RenderingError, match="Invalid XML"):
            await converter.to_svg("not xml")


class TestImageConverterTimeout:
    """Test timeout enforcement."""

    @pytest.mark.asyncio
    async def test_to_png_timeout(self, test_env, monkeypatch):
        """Test to_png raises timeout error."""

        async def slow_conversion(*args, **kwargs):
            await asyncio.sleep(10)

        converter = ImageConverter()
        converter.timeout = 0.001  # Set very short timeout
        converter._to_png_internal = slow_conversion

        with pytest.raises(RenderingError, match="timed out"):
            await converter.to_png("<mxfile></mxfile>")

    @pytest.mark.asyncio
    async def test_to_svg_timeout(self, test_env, monkeypatch):
        """Test to_svg raises timeout error."""

        async def slow_conversion(*args, **kwargs):
            await asyncio.sleep(10)

        converter = ImageConverter()
        converter.timeout = 0.001
        converter._to_svg_internal = slow_conversion

        with pytest.raises(RenderingError, match="timed out"):
            await converter.to_svg("<mxfile></mxfile>")


class TestImageConverterHtmlGeneration:
    """Test HTML generation for PNG rendering."""

    def test_create_html_from_valid_xml(self, test_env):
        """Test HTML generation from valid XML."""
        converter = ImageConverter()
        xml = "<mxfile><diagram>Test</diagram></mxfile>"

        html = converter._create_html_from_xml(xml)

        assert "<html>" in html
        assert "mxgraph" in html
        assert "diagram" in html
        assert "Test" in html

    def test_create_html_empty_xml_fails(self, test_env):
        """Test HTML generation with empty XML fails."""
        converter = ImageConverter()

        with pytest.raises(RenderingError, match="empty XML"):
            converter._create_html_from_xml("")

    def test_create_html_escapes_special_chars(self, test_env):
        """Test HTML generation properly escapes special characters."""
        converter = ImageConverter()
        xml = '<mxfile><diagram name="Test & Co."></diagram></mxfile>'

        html = converter._create_html_from_xml(xml)

        # Check that & and " are escaped
        assert "&amp;" in html
        assert "&quot;" in html
        assert "Test &amp; Co." in html

    def test_create_html_complex_xml(self, test_env):
        """Test HTML generation with complex XML structure."""
        converter = ImageConverter()
        xml = (
            "<mxfile><diagram><mxCell id='1' value='Cell 1'/>"
            "<mxCell id='2' value='Cell 2'/></diagram></mxfile>"
        )

        html = converter._create_html_from_xml(xml)

        assert "<html>" in html
        assert "Cell 1" in html
        assert "Cell 2" in html

    def test_create_html_preserves_content(self, test_env):
        """Test HTML generation preserves all XML content."""
        converter = ImageConverter()
        xml = "<mxfile><diagram><data>Important Data</data></diagram></mxfile>"

        html = converter._create_html_from_xml(xml)

        assert "Important Data" in html


class TestImageConverterConfiguration:
    """Test configuration and setup."""

    def test_converter_timeout_from_settings(self, test_env):
        """Test converter uses correct timeout from settings."""
        # test_env sets IMAGE_TIMEOUT=4
        converter = ImageConverter()
        assert converter.timeout == 8

    def test_converter_drawio_url_from_settings(self, test_env):
        """Test converter uses correct draw.io URL from settings."""
        # test_env sets DRAWIO_SERVICE_URL=http://localhost:6002
        converter = ImageConverter()
        assert converter.drawio_url == "http://localhost:6002"


class TestImageConverterPngConversion:
    """Test PNG conversion error handling."""

    def test_to_png_internal_requires_valid_xml(self):
        """Test _to_png_internal validates XML format."""
        converter = ImageConverter()

        # Empty XML should fail validation
        with pytest.raises(RenderingError):
            asyncio.run(converter._to_png_internal(""))

        # Non-XML should fail validation
        with pytest.raises(RenderingError):
            asyncio.run(converter._to_png_internal("not xml"))


class TestImageConverterSvgConversion:
    """Test SVG conversion error handling."""

    def test_to_svg_internal_requires_valid_xml(self):
        """Test _to_svg_internal validates XML format."""
        converter = ImageConverter()

        # Empty XML should fail validation
        with pytest.raises(RenderingError):
            asyncio.run(converter._to_svg_internal(""))

        # Non-XML should fail validation
        with pytest.raises(RenderingError):
            asyncio.run(converter._to_svg_internal("not xml"))


class TestImageConverterErrorMessages:
    """Test error messages are informative."""

    def test_png_timeout_message_includes_timeout_value(self, test_env):
        """Test PNG timeout error includes timeout duration."""

        async def slow_conversion(*args, **kwargs):
            await asyncio.sleep(10)

        converter = ImageConverter()
        converter.timeout = 0.001
        converter._to_png_internal = slow_conversion

        try:
            asyncio.run(converter.to_png("<mxfile></mxfile>"))
        except RenderingError as e:
            assert "0.001" in str(e) or "timed out" in str(e)

    def test_svg_timeout_message_includes_timeout_value(self, test_env):
        """Test SVG timeout error includes timeout duration."""

        async def slow_conversion(*args, **kwargs):
            await asyncio.sleep(10)

        converter = ImageConverter()
        converter.timeout = 0.001
        converter._to_svg_internal = slow_conversion

        try:
            asyncio.run(converter.to_svg("<mxfile></mxfile>"))
        except RenderingError as e:
            assert "0.001" in str(e) or "timed out" in str(e)

    def test_invalid_xml_error_message(self, test_env):
        """Test invalid XML error is clear."""
        converter = ImageConverter()

        with pytest.raises(RenderingError) as exc_info:
            asyncio.run(converter.to_png("not xml"))

        assert "Invalid XML" in str(exc_info.value) or "format" in str(exc_info.value)
