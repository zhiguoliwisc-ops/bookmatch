from abc import ABC, abstractmethod

from bookmatch.models.book import BookInput, EnrichedBook


class BookInformationService(ABC):
    """Interface for services that enrich book information."""

    @abstractmethod
    def enrich(self, book: BookInput) -> EnrichedBook:
        """Enrich incomplete book information."""
        pass