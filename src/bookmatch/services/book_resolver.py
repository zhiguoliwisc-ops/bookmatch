from abc import ABC, abstractmethod

from bookmatch.models.book import BookInput, EnrichedBook


class BookResolver(ABC):
    """Interface for resolving a book input to an identified book."""

    @abstractmethod
    def resolve(
        self,
        book: BookInput,
    ) -> EnrichedBook:
        """Resolve a book input to an identified enriched book."""
        raise NotImplementedError