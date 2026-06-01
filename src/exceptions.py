"""
Custom exceptions for TestLink client operations.
"""


class TestLinkException(Exception):
    """Base exception for all TestLink errors."""
    
    def __init__(self, message: str, details: str = None):
        self.message = message
        self.details = details
        super().__init__(self.message)
    
    def __str__(self):
        if self.details:
            return f"{self.message}\nDetails: {self.details}"
        return self.message


class PfsErrorException(TestLinkException):
    """
    Raised when PFS returns an Error response.
    Indicates the request did not complete successfully.
    """
    pass


class PfsFailureException(TestLinkException):
    """
    Raised when PFS returns a Failure response.
    Indicates the request completed but validation failed.
    """
    pass


class PfsWarningException(TestLinkException):
    """
    Raised when PFS returns a Warning response.
    Indicates the request completed but with caution.
    """
    pass


class ConnectionException(TestLinkException):
    """Raised when connection to PFS server fails."""
    pass


class TimeoutException(TestLinkException):
    """Raised when a request times out."""
    pass


class ConfigurationException(TestLinkException):
    """Raised when configuration is invalid or missing."""
    pass


class ValidationException(TestLinkException):
    """Raised when parameter validation fails."""
    pass


class ProtocolException(TestLinkException):
    """Raised when protocol formatting or parsing fails."""
    pass
