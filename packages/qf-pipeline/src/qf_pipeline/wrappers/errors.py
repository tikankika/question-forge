"""Custom exceptions for qf-pipeline wrappers.

These exceptions wrap QTI-Generator errors in MCP-friendly formats.
"""

from typing import Optional


class WrapperError(Exception):
    """Base exception for wrapper errors."""

    def __init__(self, message: str, source_error: Optional[Exception] = None):
        super().__init__(message)
        self.source_error = source_error

    def to_dict(self) -> dict:
        """Convert to dictionary for MCP responses."""
        return {
            "error": self.__class__.__name__,
            "message": str(self),
            "source": str(self.source_error) if self.source_error else None,
        }


class ParsingError(WrapperError):
    """Error during markdown parsing."""

    pass


class GenerationError(WrapperError):
    """Error during XML generation."""

    pass


class PackagingError(WrapperError):
    """Error during package creation."""

    pass


class ValidationError(WrapperError):
    """Error during content validation."""

    pass


class ResourceError(WrapperError):
    """Error with media resources."""

    pass
