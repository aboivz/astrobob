"""Custom exceptions for AstroBob."""


class AstroBobError(Exception):
    """Base exception for all AstroBob errors."""
    pass


class ConfigError(AstroBobError):
    """Raised when configuration is invalid or missing."""
    pass


class AstraConnectionError(AstroBobError):
    """Raised when connection to AstraDB fails."""
    pass


class MemoryNotFoundError(AstroBobError):
    """Raised when a requested memory document is not found."""
    pass


class ValidationError(AstroBobError):
    """Raised when data validation fails."""
    pass

# Made with Bob
