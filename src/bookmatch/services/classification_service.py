from abc import ABC, abstractmethod

from bookmatch.models.book import BookInput
from bookmatch.models.classification import BookClassification


class ClassificationService(ABC):
    """Interface for book classification services."""

    @abstractmethod
    def classify(self, book: BookInput) -> BookClassification:
        """Classify a book by recommended age group and reading difficulty."""
        pass