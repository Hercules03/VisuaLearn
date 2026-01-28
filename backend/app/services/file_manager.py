"""File Manager service for handling temporary file storage and cleanup."""

import asyncio
import uuid
from datetime import datetime, timedelta
from pathlib import Path

from loguru import logger

from app.config import settings
from app.errors import FileOperationError


class FileManager:
    """Service for managing temporary diagram files."""

    def __init__(self):
        """Initialize file manager with configuration."""
        self.temp_dir = Path(settings.temp_dir)
        self.ttl_seconds = settings.temp_file_ttl
        self.cleanup_interval = settings.cleanup_interval
        self.max_file_size = settings.max_file_size

        # Create temp directory if it doesn't exist
        self.temp_dir.mkdir(parents=True, exist_ok=True)

        logger.info(
            "File manager initialized",
            temp_dir=str(self.temp_dir),
            ttl_seconds=self.ttl_seconds,
            max_file_size=self.max_file_size,
        )

    async def save_file(self, content: bytes, file_format: str = "png") -> str:
        """Save diagram file to temporary storage.

        Saves a file with automatic cleanup after TTL expires.

        Args:
            content: File content as bytes
            file_format: File extension (png, svg, xml)

        Returns:
            Filename (UUID with extension) for retrieval

        Raises:
            FileOperationError: If file operations fail
        """
        # Validate file format
        if file_format not in ["png", "svg", "xml"]:
            raise FileOperationError(
                f"Invalid file format: {file_format}. Must be png, svg, or xml."
            )

        # Validate file size
        file_size = len(content)
        if file_size > self.max_file_size:
            raise FileOperationError(
                f"File size {file_size} exceeds maximum {self.max_file_size}"
            )

        # Generate unique filename
        file_id = str(uuid.uuid4())
        filename = f"{file_id}.{file_format}"
        filepath = self.temp_dir / filename

        try:
            # Save file
            filepath.write_bytes(content)
            logger.info(
                "File saved",
                filename=filename,
                size_bytes=file_size,
                format=file_format,
            )

            # Schedule cleanup after TTL
            asyncio.create_task(self._cleanup_file_after_ttl(filepath))

            return filename
        except IOError as e:
            logger.error(f"Failed to save file: {e}")
            raise FileOperationError(f"Failed to save file: {str(e)}")

    async def save_text_file(self, content: str, file_format: str = "xml") -> str:
        """Save text content to temporary storage.

        Args:
            content: Text content as string
            file_format: File extension (xml, txt)

        Returns:
            Filename (UUID with extension) for retrieval

        Raises:
            FileOperationError: If file operations fail
        """
        # Convert to bytes
        content_bytes = content.encode("utf-8")
        return await self.save_file(content_bytes, file_format)

    async def get_file(self, filename: str) -> bytes:
        """Retrieve file from temporary storage.

        Args:
            filename: Filename to retrieve

        Returns:
            File content as bytes

        Raises:
            FileOperationError: If file not found or read fails
        """
        # Validate filename format (prevent path traversal)
        if "/" in filename or "\\" in filename or filename.startswith("."):
            raise FileOperationError(f"Invalid filename: {filename}")

        filepath = self.temp_dir / filename

        if not filepath.exists():
            raise FileOperationError(f"File not found: {filename}")

        try:
            content = filepath.read_bytes()
            logger.info("File retrieved", filename=filename, size_bytes=len(content))
            return content
        except IOError as e:
            logger.error(f"Failed to read file {filename}: {e}")
            raise FileOperationError(f"Failed to read file: {str(e)}")

    async def delete_file(self, filename: str) -> None:
        """Delete file from temporary storage.

        Args:
            filename: Filename to delete

        Raises:
            FileOperationError: If deletion fails
        """
        # Validate filename format
        if "/" in filename or "\\" in filename or filename.startswith("."):
            raise FileOperationError(f"Invalid filename: {filename}")

        filepath = self.temp_dir / filename

        try:
            if filepath.exists():
                filepath.unlink()
                logger.info("File deleted", filename=filename)
        except IOError as e:
            logger.error(f"Failed to delete file {filename}: {e}")
            raise FileOperationError(f"Failed to delete file: {str(e)}")

    async def get_file_metadata(self, filename: str) -> dict:
        """Get metadata for a file.

        Args:
            filename: Filename to get metadata for

        Returns:
            Dictionary with file metadata (size, created, modified)

        Raises:
            FileOperationError: If file not found
        """
        # Validate filename format
        if "/" in filename or "\\" in filename or filename.startswith("."):
            raise FileOperationError(f"Invalid filename: {filename}")

        filepath = self.temp_dir / filename

        if not filepath.exists():
            raise FileOperationError(f"File not found: {filename}")

        try:
            stat = filepath.stat()
            return {
                "filename": filename,
                "size_bytes": stat.st_size,
                "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "format": filepath.suffix.lstrip("."),
            }
        except OSError as e:
            logger.error(f"Failed to get metadata for {filename}: {e}")
            raise FileOperationError(f"Failed to get file metadata: {str(e)}")

    async def cleanup_expired_files(self) -> int:
        """Clean up files that have exceeded TTL.

        Returns:
            Number of files deleted

        Raises:
            FileOperationError: If cleanup fails
        """
        deleted_count = 0
        now = datetime.now()
        ttl_delta = timedelta(seconds=self.ttl_seconds)

        try:
            for filepath in self.temp_dir.glob("*"):
                if not filepath.is_file():
                    continue

                # Check if file is older than TTL
                modified_time = datetime.fromtimestamp(filepath.stat().st_mtime)
                if now - modified_time > ttl_delta:
                    filepath.unlink()
                    deleted_count += 1
                    logger.debug(f"Cleaned up expired file: {filepath.name}")

            if deleted_count > 0:
                logger.info(f"Cleanup completed, deleted {deleted_count} files")

            return deleted_count
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            raise FileOperationError(f"Cleanup operation failed: {str(e)}")

    async def _cleanup_file_after_ttl(self, filepath: Path) -> None:
        """Internal cleanup task for individual file after TTL expires.

        Args:
            filepath: Path to file to clean up
        """
        try:
            # Wait for TTL duration
            await asyncio.sleep(self.ttl_seconds)

            # Delete file if it still exists
            if filepath.exists():
                filepath.unlink()
                logger.debug(f"Auto-deleted expired file: {filepath.name}")
        except Exception as e:
            logger.error(f"Failed to auto-cleanup file {filepath.name}: {e}")

    def get_temp_dir_stats(self) -> dict:
        """Get statistics about temporary directory.

        Returns:
            Dictionary with directory stats (file_count, total_size)
        """
        try:
            file_count = 0
            total_size = 0

            for filepath in self.temp_dir.glob("*"):
                if filepath.is_file():
                    file_count += 1
                    total_size += filepath.stat().st_size

            return {
                "temp_dir": str(self.temp_dir),
                "file_count": file_count,
                "total_size_bytes": total_size,
                "max_size_bytes": self.max_file_size,
            }
        except Exception as e:
            logger.error(f"Failed to get directory stats: {e}")
            return {
                "error": str(e),
            }
