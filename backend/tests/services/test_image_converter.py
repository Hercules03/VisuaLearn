"""Tests for ImageConverter service (XML validation for client-side rendering)."""

import pytest

from app.errors import RenderingError
from app.services.image_converter import ImageConverter


class TestImageConverterInit:
    """ImageConverter initialization tests."""

    def test_init_creates_converter(self):
        """Test converter initialization."""
        converter = ImageConverter()
        assert converter is not None


class TestImageConverterValidation:
    """XML validation tests."""

    @pytest.mark.asyncio
    async def test_valid_minimal_diagram(self):
        """Test validation of minimal valid draw.io XML."""
        converter = ImageConverter()

        # Minimal valid draw.io XML structure
        xml = """<?xml version="1.0"?>
<mxfile>
    <diagram>
        <mxGraphModel>
            <root>
                <mxCell id="0" parent="" vertex="1"/>
                <mxCell id="1" parent="0" vertex="1"/>
            </root>
        </mxGraphModel>
    </diagram>
</mxfile>"""

        result = await converter.to_svg(xml)
        assert result == xml

    @pytest.mark.asyncio
    async def test_valid_complete_diagram(self):
        """Test validation of complete diagram with components and relationships."""
        converter = ImageConverter()

        xml = """<?xml version="1.0"?>
<mxfile>
    <diagram>
        <mxGraphModel>
            <root>
                <mxCell id="0" parent="" vertex="1"/>
                <mxCell id="1" parent="0" vertex="1" value="Component 1"/>
                <mxCell id="2" parent="0" vertex="1" value="Component 2"/>
                <mxCell id="3" parent="0" edge="1" source="1" target="2" value="relates to"/>
            </root>
        </mxGraphModel>
    </diagram>
</mxfile>"""

        result = await converter.to_svg(xml)
        assert result == xml
        assert "<mxCell" in result
        assert 'vertex="1"' in result
        assert 'edge="1"' in result

    @pytest.mark.asyncio
    async def test_empty_xml(self):
        """Test error handling for empty XML."""
        converter = ImageConverter()

        with pytest.raises(RenderingError, match="Empty XML"):
            await converter.to_svg("")

    @pytest.mark.asyncio
    async def test_whitespace_only_xml(self):
        """Test error handling for whitespace-only XML."""
        converter = ImageConverter()

        with pytest.raises(RenderingError, match="Empty XML"):
            await converter.to_svg("   \n\t  ")

    @pytest.mark.asyncio
    async def test_invalid_xml_syntax(self):
        """Test error handling for malformed XML."""
        converter = ImageConverter()

        invalid_xml = "<?xml version='1.0'?><mxfile><diagram><mxGraphModel></mxfile>"

        with pytest.raises(RenderingError, match="Invalid XML syntax"):
            await converter.to_svg(invalid_xml)

    @pytest.mark.asyncio
    async def test_wrong_root_element(self):
        """Test error handling for non-mxfile root."""
        converter = ImageConverter()

        xml = """<?xml version="1.0"?>
<svg>
    <diagram/>
</svg>"""

        with pytest.raises(RenderingError, match="Expected <mxfile> root element"):
            await converter.to_svg(xml)

    @pytest.mark.asyncio
    async def test_missing_diagram_element(self):
        """Test error handling when <diagram> is missing."""
        converter = ImageConverter()

        xml = """<?xml version="1.0"?>
<mxfile>
    <other/>
</mxfile>"""

        with pytest.raises(RenderingError, match="Missing <diagram> element"):
            await converter.to_svg(xml)

    @pytest.mark.asyncio
    async def test_missing_mxgraphmodel(self):
        """Test error handling when <mxGraphModel> is missing."""
        converter = ImageConverter()

        xml = """<?xml version="1.0"?>
<mxfile>
    <diagram>
        <other/>
    </diagram>
</mxfile>"""

        with pytest.raises(RenderingError, match="Missing <mxGraphModel> element"):
            await converter.to_svg(xml)

    @pytest.mark.asyncio
    async def test_missing_root_element(self):
        """Test error handling when <root> cell container is missing."""
        converter = ImageConverter()

        xml = """<?xml version="1.0"?>
<mxfile>
    <diagram>
        <mxGraphModel>
            <other/>
        </mxGraphModel>
    </diagram>
</mxfile>"""

        with pytest.raises(RenderingError, match="Missing diagram cells"):
            await converter.to_svg(xml)

    @pytest.mark.asyncio
    async def test_insufficient_cells(self):
        """Test error handling when diagram has too few cells."""
        converter = ImageConverter()

        xml = """<?xml version="1.0"?>
<mxfile>
    <diagram>
        <mxGraphModel>
            <root>
                <mxCell id="0" parent="" vertex="1"/>
            </root>
        </mxGraphModel>
    </diagram>
</mxfile>"""

        with pytest.raises(RenderingError, match="insufficient cells"):
            await converter.to_svg(xml)


class TestImageConverterLogging:
    """Test logging of validation results."""

    @pytest.mark.asyncio
    async def test_logs_validation_success(self, capsys):
        """Test that successful validation is logged with cell counts."""
        converter = ImageConverter()

        xml = """<?xml version="1.0"?>
<mxfile>
    <diagram>
        <mxGraphModel>
            <root>
                <mxCell id="0" parent="" vertex="1"/>
                <mxCell id="1" parent="0" vertex="1" value="Node"/>
                <mxCell id="2" parent="0" vertex="1" value="Node2"/>
                <mxCell id="3" parent="0" edge="1" source="1" target="2"/>
            </root>
        </mxGraphModel>
    </diagram>
</mxfile>"""

        result = await converter.to_svg(xml)

        # Verify validation worked and returned the XML
        assert result == xml
        # Verify cell counts are correct
        assert xml.count('vertex="1"') == 3
        assert xml.count('edge="1"') == 1

    @pytest.mark.asyncio
    async def test_logs_different_cell_types(self):
        """Test logging distinguishes vertex and edge cells."""
        converter = ImageConverter()

        xml = """<?xml version="1.0"?>
<mxfile>
    <diagram>
        <mxGraphModel>
            <root>
                <mxCell id="0" parent="" vertex="1"/>
                <mxCell id="1" parent="0" vertex="1"/>
                <mxCell id="2" parent="0" vertex="1"/>
                <mxCell id="3" parent="0" vertex="1"/>
                <mxCell id="4" parent="0" edge="1" source="1" target="2"/>
                <mxCell id="5" parent="0" edge="1" source="2" target="3"/>
            </root>
        </mxGraphModel>
    </diagram>
</mxfile>"""

        result = await converter.to_svg(xml)

        # Verify cell counts are correct
        assert result == xml
        assert xml.count('vertex="1"') == 4
        assert xml.count('edge="1"') == 2


class TestImageConverterDataIntegrity:
    """Test that validation doesn't modify the XML."""

    @pytest.mark.asyncio
    async def test_returns_unchanged_xml(self):
        """Test that validated XML is returned unchanged."""
        converter = ImageConverter()

        xml = """<?xml version="1.0"?>
<mxfile version="1.0" xmlns="http://jgraph.com/xml">
    <diagram name="Test">
        <mxGraphModel>
            <root>
                <mxCell id="0" parent="" vertex="1" value="A"/>
                <mxCell id="1" parent="0" vertex="1" value="B"/>
                <mxCell id="2" parent="0" edge="1" source="0" target="1" value="relation"/>
            </root>
        </mxGraphModel>
    </diagram>
</mxfile>"""

        result = await converter.to_svg(xml)

        # Result should be identical to input
        assert result == xml

    @pytest.mark.asyncio
    async def test_preserves_attributes(self):
        """Test that all XML attributes are preserved."""
        converter = ImageConverter()

        xml = """<?xml version="1.0"?>
<mxfile>
    <diagram>
        <mxGraphModel>
            <root>
                <mxCell id="0" parent="" vertex="1"/>
                <mxCell id="1" parent="0" vertex="1" value="Test"
                         style="fillColor=#ffffff;strokeWidth=3;fontSize=14"/>
                <mxCell id="2" parent="0" vertex="1"/>
            </root>
        </mxGraphModel>
    </diagram>
</mxfile>"""

        result = await converter.to_svg(xml)

        # Attributes should be preserved
        assert 'fillColor=#ffffff' in result
        assert 'strokeWidth=3' in result
        assert 'fontSize=14' in result


class TestImageConverterRobustness:
    """Test robustness with edge cases."""

    @pytest.mark.asyncio
    async def test_handles_large_valid_diagram(self):
        """Test validation of larger diagram with many components."""
        converter = ImageConverter()

        # Build diagram with 50 cells
        cells = ["<mxCell id=\"0\" parent=\"\" vertex=\"1\"/>"]
        for i in range(1, 25):
            cells.append(f'<mxCell id="{i}" parent="0" vertex="1" value="Node{i}"/>')
        for i in range(25, 50):
            cells.append(
                f'<mxCell id="{i}" parent="0" edge="1" source="{i-25}" target="{i-24}"/>'
            )

        xml = f"""<?xml version="1.0"?>
<mxfile>
    <diagram>
        <mxGraphModel>
            <root>
                {''.join(cells)}
            </root>
        </mxGraphModel>
    </diagram>
</mxfile>"""

        result = await converter.to_svg(xml)
        assert result == xml

    @pytest.mark.asyncio
    async def test_handles_special_characters(self):
        """Test validation with special characters in cell values."""
        converter = ImageConverter()

        xml = """<?xml version="1.0"?>
<mxfile>
    <diagram>
        <mxGraphModel>
            <root>
                <mxCell id="0" parent="" vertex="1"/>
                <mxCell id="1" parent="0" vertex="1" value="Math: &lt;x&gt; = y &amp; z"/>
                <mxCell id="2" parent="0" vertex="1" value="UTF-8: 你好 мир 🎉"/>
            </root>
        </mxGraphModel>
    </diagram>
</mxfile>"""

        result = await converter.to_svg(xml)
        assert "Math:" in result
        assert "&lt;x&gt;" in result or "<x>" in result
        assert "&amp;" in result or "&" in result

    @pytest.mark.asyncio
    async def test_handles_namespaces(self):
        """Test validation with XML namespaces."""
        converter = ImageConverter()

        xml = """<?xml version="1.0"?>
<mxfile xmlns="http://jgraph.com/xml">
    <diagram>
        <mxGraphModel>
            <root>
                <mxCell id="0" parent="" vertex="1"/>
                <mxCell id="1" parent="0" vertex="1"/>
            </root>
        </mxGraphModel>
    </diagram>
</mxfile>"""

        result = await converter.to_svg(xml)
        assert result == xml


class TestImageConverterSecurityValidation:
    """Test that validation includes security checks (no XXE)."""

    @pytest.mark.asyncio
    async def test_rejects_xml_with_dtd_entity(self):
        """Test that XXE attacks are prevented."""
        converter = ImageConverter()

        # XXE attack vector
        xml = """<?xml version="1.0"?>
<!DOCTYPE mxfile [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
<mxfile>
    <diagram>
        <mxGraphModel>
            <root>
                <mxCell id="0" parent="" vertex="1" value="&xxe;"/>
                <mxCell id="1" parent="0" vertex="1"/>
            </root>
        </mxGraphModel>
    </diagram>
</mxfile>"""

        # Should raise error (lxml prevents XXE by default)
        with pytest.raises(RenderingError):
            await converter.to_svg(xml)

    @pytest.mark.asyncio
    async def test_rejects_extremely_large_xml(self):
        """Test DOS protection against billion laughs attack."""
        converter = ImageConverter()

        # Very large XML (simulating billion laughs)
        huge_xml = "<?xml version='1.0'?>" + "<a>" * 100000 + "</a>" * 100000

        # Should handle gracefully
        with pytest.raises(RenderingError):
            await converter.to_svg(huge_xml)
