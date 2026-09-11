from abc import ABC, abstractmethod

from bookmatch.models.book import EnrichedBook
from bookmatch.models.classification import BookClassification
from bookmatch.models.classification_review import ClassificationReview


class BookReviewerAgent(ABC):
    """Interface for an agent that reviews book classifications."""

    @abstractmethod
    def review(
        self,
        book: EnrichedBook,
        classification: BookClassification,
    ) -> ClassificationReview:
        """Review a book classification."""
        raise NotImplementedError