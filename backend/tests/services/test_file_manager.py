"""Tests for File Manager service."""

import asyncio

import pytest

from app.errors import FileOperationError
from app.services.file_manager import FileManager


class TestFileManagerInit:
    """Test FileManager initialization."""

    def test_init_creates_manager(self, test_env):
        """Test successful initialization creates manager."""
        manager = FileManager()
        assert manager.temp_dir is not None
        assert manager.ttl_seconds == 3600
        assert manager.max_file_size == 5242880

    def test_init_creates_temp_directory(self, test_env):
        """Test initialization creates temp directory."""
        manager = FileManager()
        assert manager.temp_dir.exists()
        assert manager.temp_dir.is_dir()


class TestFileManagerSaveFile:
    """Test FileManager.save_file() method."""

    @pytest.mark.asyncio
    async def test_save_png_file(self, test_env):
        """Test saving PNG file."""
        manager = FileManager()
        png_content = b"\x89PNG\r\n\x1a\n" + b"test" * 100

        filename = await manager.save_file(png_content, "png")

        assert filename.endswith(".png")
        assert len(filename.split(".")[0]) == 36  # UUID length

        # Verify file exists
        filepath = manager.temp_dir / filename
        assert filepath.exists()
        assert filepath.read_bytes() == png_content

    @pytest.mark.asyncio
    async def test_save_svg_file(self, test_env):
        """Test saving SVG file."""
        manager = FileManager()
        svg_content = b"<svg></svg>"

        filename = await manager.save_file(svg_content, "svg")

        assert filename.endswith(".svg")
        filepath = manager.temp_dir / filename
        assert filepath.read_bytes() == svg_content

    @pytest.mark.asyncio
    async def test_save_xml_file(self, test_env):
        """Test saving XML file."""
        manager = FileManager()
        xml_content = b"<mxfile></mxfile>"

        filename = await manager.save_file(xml_content, "xml")

        assert filename.endswith(".xml")
        filepath = manager.temp_dir / filename
        assert filepath.read_bytes() == xml_content

    @pytest.mark.asyncio
    async def test_save_invalid_format(self, test_env):
        """Test saving with invalid format fails."""
        manager = FileManager()

        with pytest.raises(FileOperationError, match="Invalid file format"):
            await manager.save_file(b"content", "pdf")

    @pytest.mark.asyncio
    async def test_save_oversized_file(self, test_env):
        """Test saving oversized file fails."""
        manager = FileManager()
        # Create content larger than max_file_size
        large_content = b"x" * (manager.max_file_size + 1)

        with pytest.raises(FileOperationError, match="exceeds maximum"):
            await manager.save_file(large_content, "png")

    @pytest.mark.asyncio
    async def test_save_empty_file(self, test_env):
        """Test saving empty file succeeds."""
        manager = FileManager()

        filename = await manager.save_file(b"", "xml")

        assert filename.endswith(".xml")
        filepath = manager.temp_dir / filename
        assert filepath.read_bytes() == b""


class TestFileManagerSaveTextFile:
    """Test FileManager.save_text_file() method."""

    @pytest.mark.asyncio
    async def test_save_xml_text(self, test_env):
        """Test saving XML text file."""
        manager = FileManager()
        xml_text = "<mxfile><diagram>Test</diagram></mxfile>"

        filename = await manager.save_text_file(xml_text, "xml")

        assert filename.endswith(".xml")
        filepath = manager.temp_dir / filename
        assert filepath.read_text() == xml_text

    @pytest.mark.asyncio
    async def test_save_text_file_default_format(self, test_env):
        """Test saving text file with default XML format."""
        manager = FileManager()
        text = "<test>content</test>"

        filename = await manager.save_text_file(text)

        assert filename.endswith(".xml")

    @pytest.mark.asyncio
    async def test_save_text_with_special_chars(self, test_env):
        """Test saving text with special characters."""
        manager = FileManager()
        text = "Special chars: é, ñ, 中文, 🎨"

        filename = await manager.save_text_file(text, "xml")

        filepath = manager.temp_dir / filename
        assert filepath.read_text(encoding="utf-8") == text


class TestFileManagerGetFile:
    """Test FileManager.get_file() method."""

    @pytest.mark.asyncio
    async def test_get_existing_file(self, test_env):
        """Test retrieving existing file."""
        manager = FileManager()
        original_content = b"test content"

        filename = await manager.save_file(original_content, "png")
        retrieved_content = await manager.get_file(filename)

        assert retrieved_content == original_content

    @pytest.mark.asyncio
    async def test_get_nonexistent_file(self, test_env):
        """Test retrieving nonexistent file fails."""
        manager = FileManager()

        with pytest.raises(FileOperationError, match="not found"):
            await manager.get_file("nonexistent.png")

    @pytest.mark.asyncio
    async def test_get_file_path_traversal_prevention(self, test_env):
        """Test path traversal attacks are prevented."""
        manager = FileManager()

        with pytest.raises(FileOperationError, match="Invalid filename"):
            await manager.get_file("../../../etc/passwd")

    @pytest.mark.asyncio
    async def test_get_file_with_slash(self, test_env):
        """Test filenames with slashes are rejected."""
        manager = FileManager()

        with pytest.raises(FileOperationError, match="Invalid filename"):
            await manager.get_file("subdir/file.png")

    @pytest.mark.asyncio
    async def test_get_file_starting_with_dot(self, test_env):
        """Test filenames starting with dot are rejected."""
        manager = FileManager()

        with pytest.raises(FileOperationError, match="Invalid filename"):
            await manager.get_file(".hidden/file.png")


class TestFileManagerDeleteFile:
    """Test FileManager.delete_file() method."""

    @pytest.mark.asyncio
    async def test_delete_existing_file(self, test_env):
        """Test deleting existing file."""
        manager = FileManager()

        filename = await manager.save_file(b"content", "png")
        filepath = manager.temp_dir / filename
        assert filepath.exists()

        await manager.delete_file(filename)
        assert not filepath.exists()

    @pytest.mark.asyncio
    async def test_delete_nonexistent_file(self, test_env):
        """Test deleting nonexistent file doesn't fail."""
        manager = FileManager()

        # Should not raise error
        await manager.delete_file("nonexistent.png")

    @pytest.mark.asyncio
    async def test_delete_file_path_traversal_prevention(self, test_env):
        """Test path traversal attacks are prevented."""
        manager = FileManager()

        with pytest.raises(FileOperationError, match="Invalid filename"):
            await manager.delete_file("../../../etc/passwd")


class TestFileManagerMetadata:
    """Test FileManager.get_file_metadata() method."""

    @pytest.mark.asyncio
    async def test_get_metadata_existing_file(self, test_env):
        """Test getting metadata for existing file."""
        manager = FileManager()
        content = b"test content"

        filename = await manager.save_file(content, "png")
        metadata = await manager.get_file_metadata(filename)

        assert metadata["filename"] == filename
        assert metadata["size_bytes"] == len(content)
        assert metadata["format"] == "png"
        assert "created_at" in metadata
        assert "modified_at" in metadata

    @pytest.mark.asyncio
    async def test_get_metadata_nonexistent_file(self, test_env):
        """Test getting metadata for nonexistent file fails."""
        manager = FileManager()

        with pytest.raises(FileOperationError, match="not found"):
            await manager.get_file_metadata("nonexistent.png")

    @pytest.mark.asyncio
    async def test_get_metadata_path_traversal_prevention(self, test_env):
        """Test path traversal attacks are prevented."""
        manager = FileManager()

        with pytest.raises(FileOperationError, match="Invalid filename"):
            await manager.get_file_metadata("../../../etc/passwd")


class TestFileManagerCleanup:
    """Test FileManager.cleanup_expired_files() method."""

    @pytest.mark.asyncio
    async def test_cleanup_no_files(self, test_env):
        """Test cleanup with no files."""
        manager = FileManager()

        deleted = await manager.cleanup_expired_files()
        assert deleted == 0

    @pytest.mark.asyncio
    async def test_cleanup_recent_file(self, test_env):
        """Test cleanup doesn't delete recent files."""
        manager = FileManager()

        filename = await manager.save_file(b"content", "png")
        deleted = await manager.cleanup_expired_files()

        assert deleted == 0  # File is recent, shouldn't be deleted
        assert (manager.temp_dir / filename).exists()

    @pytest.mark.asyncio
    async def test_cleanup_old_file(self, test_env, monkeypatch):
        """Test cleanup deletes expired files."""

        manager = FileManager()

        # Set TTL to 0 so all files are immediately expired
        original_ttl = manager.ttl_seconds
        manager.ttl_seconds = 0

        filename = await manager.save_file(b"content", "png")
        filepath = manager.temp_dir / filename

        # Wait longer to ensure file is definitely expired
        await asyncio.sleep(0.1)

        deleted = await manager.cleanup_expired_files()

        # Restore original TTL
        manager.ttl_seconds = original_ttl

        assert deleted >= 1  # At least 1 file should be deleted
        assert not filepath.exists()


class TestFileManagerDirectoryStats:
    """Test FileManager.get_temp_dir_stats() method."""

    def test_stats_empty_directory(self, test_env):
        """Test stats for empty directory."""
        manager = FileManager()
        stats = manager.get_temp_dir_stats()

        assert stats["temp_dir"] is not None
        assert stats["file_count"] == 0
        assert stats["total_size_bytes"] == 0

    @pytest.mark.asyncio
    async def test_stats_with_files(self, test_env):
        """Test stats with files in directory."""
        manager = FileManager()

        content1 = b"content1"
        content2 = b"content2" * 10

        await manager.save_file(content1, "png")
        await manager.save_file(content2, "svg")

        stats = manager.get_temp_dir_stats()

        assert stats["file_count"] == 2
        assert stats["total_size_bytes"] == len(content1) + len(content2)


class TestFileManagerIntegration:
    """Integration tests for File Manager."""

    @pytest.mark.asyncio
    async def test_save_and_retrieve_cycle(self, test_env):
        """Test complete save and retrieve cycle."""
        manager = FileManager()
        original_content = b"<mxfile><diagram>Test</diagram></mxfile>"

        # Save file
        filename = await manager.save_file(original_content, "xml")
        assert filename is not None

        # Retrieve file
        retrieved = await manager.get_file(filename)
        assert retrieved == original_content

        # Get metadata
        metadata = await manager.get_file_metadata(filename)
        assert metadata["size_bytes"] == len(original_content)

        # Delete file
        await manager.delete_file(filename)
        with pytest.raises(FileOperationError):
            await manager.get_file(filename)

    @pytest.mark.asyncio
    async def test_multiple_files(self, test_env):
        """Test managing multiple files."""
        manager = FileManager()

        # Create multiple files
        filenames = []
        for i in range(3):
            filename = await manager.save_file(f"content{i}".encode(), "png")
            filenames.append(filename)

        # Verify all exist
        for filename in filenames:
            assert (manager.temp_dir / filename).exists()

        # Delete one
        await manager.delete_file(filenames[0])
        assert not (manager.temp_dir / filenames[0]).exists()
        assert (manager.temp_dir / filenames[1]).exists()
        assert (manager.temp_dir / filenames[2]).exists()
