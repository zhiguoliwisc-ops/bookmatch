class InsufficientBookInformationError(Exception):
    """Raised when there is not enough information to classify a book."""


class BookNotFoundError(Exception):
    """Raised when a book cannot be found."""

class AmbiguousBookError(Exception):
    """Raised when multiple books match the input."""

class BookInformationServiceError(Exception):
    """Raised when a book information service cannot complete a request."""