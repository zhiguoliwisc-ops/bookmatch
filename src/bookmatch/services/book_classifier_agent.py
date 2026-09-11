from abc import ABC, abstractmethod

from bookmatch.models.book import EnrichedBook
from bookmatch.models.classification import BookClassification


class BookClassifierAgent(ABC):
    """Interface for an agent that classifies books."""

    @abstractmethod
    def classify(
        self,
        book: EnrichedBook,
    ) -> BookClassification:
        """Classify an enriched book."""
        raise NotImplementedError