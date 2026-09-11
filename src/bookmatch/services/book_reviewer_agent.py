from abc import ABC, abstractmethod

from bookmatch.models.book import EnrichedBook
from bookmatch.models.classification import BookClassification
from bookmatch.models.classification_review import ClassificationReview

from bookmatch.models.book import BookInput, EnrichedBook

class BookReviewerAgent(ABC):
    """Interface for an agent that reviews book classifications."""

    @abstractmethod
    def review(
        self,
        original_input: BookInput,
        book: EnrichedBook,
        classification: BookClassification,
    ) -> ClassificationReview:
        """Review a book classification."""
        raise NotImplementedError