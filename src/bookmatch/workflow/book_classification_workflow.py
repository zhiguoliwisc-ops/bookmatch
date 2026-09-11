from bookmatch.models.book import BookInput
from bookmatch.models.result import BookMatchResult
from bookmatch.services.book_resolver import BookResolver
from bookmatch.services.classification_service import (
    ClassificationService,
)
from bookmatch.models.book import BookInput, EnrichedBook
from bookmatch.models.classification import BookClassification

class BookClassificationWorkflow:
    """Coordinate book resolution and classification."""

    def __init__(
        self,
        book_resolver: BookResolver,
        classification_service: ClassificationService,
    ) -> None:
        self.book_resolver = book_resolver
        self.classification_service = classification_service

    def run(self, book: BookInput) -> BookMatchResult:
        """Resolve a book and classify it."""

        enriched_book = self.book_resolver.resolve(book)

        classification = self.classification_service.classify(
            enriched_book
        )

        return BookMatchResult(
            book=enriched_book,
            classification=classification,
        )

    def classify_book(
        self,
        book: EnrichedBook,
    ) -> BookClassification:
        """Classify an already resolved book."""
        return self.classification_service.classify(book)