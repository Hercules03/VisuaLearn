"""Custom exceptions for VisuaLearn."""


class VisuaLearnError(Exception):
    """Base exception for VisuaLearn."""

    def __init__(self, message: str, details: str = None):
        """Initialize exception.

        Args:
            message: User-friendly error message
            details: Technical details for logging
        """
        self.message = message
        self.details = details or message
        super().__init__(self.message)


class InputValidationError(VisuaLearnError):
    """Raised when user input validation fails."""

    pass


class PlanningError(VisuaLearnError):
    """Raised when planning agent fails."""

    pass


class GenerationError(VisuaLearnError):
    """Raised when diagram generation fails."""

    pass


class ReviewError(VisuaLearnError):
    """Raised when review agent fails."""

    pass


class RenderingError(VisuaLearnError):
    """Raised when image rendering fails."""

    pass


class FileOperationError(VisuaLearnError):
    """Raised when file operations fail."""

    pass


class OrchestrationError(VisuaLearnError):
    """Raised when orchestration pipeline fails."""

    pass
