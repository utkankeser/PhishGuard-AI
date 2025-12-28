"""
Custom exceptions for PhishGuard AI application.
Provides a hierarchical exception structure for better error handling.
"""


class PhishGuardError(Exception):
    """Base exception for all PhishGuard errors."""
    
    def __init__(self, message: str, details: str = None):
        self.message = message
        self.details = details
        super().__init__(self.message)
    
    def __str__(self):
        if self.details:
            return f"{self.message}\nDetails: {self.details}"
        return self.message


class ConfigurationError(PhishGuardError):
    """Raised when there's a configuration or environment variable issue."""
    pass


class VectorStoreError(PhishGuardError):
    """Raised when there's an issue with the vector database."""
    pass


class LLMError(PhishGuardError):
    """Raised when there's an issue with the LLM/API."""
    pass


class EmbeddingError(PhishGuardError):
    """Raised when there's an issue with the embedding model."""
    pass
