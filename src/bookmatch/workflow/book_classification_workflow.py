from bookmatch.models.book import BookInput
from bookmatch.models.result import BookMatchResult
from bookmatch.services.book_resolver import BookResolver
from bookmatch.services.book_classifier_agent import (
    BookClassifierAgent,
)
from bookmatch.models.book import BookInput, EnrichedBook
from bookmatch.models.classification import BookClassification

class BookClassificationWorkflow:
    """Coordinate book resolution and classification."""

    def __init__(
        self,
        book_resolver: BookResolver,
        classifier_agent: BookClassifierAgent,
    ) -> None:
        self.book_resolver = book_resolver
        self.classifier_agent = classifier_agent

    def run(self, book: BookInput) -> BookMatchResult:
        """Resolve a book and classify it."""

        enriched_book = self.book_resolver.resolve(book)

        classification = self.classifier_agent.classify(
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
        return self.classifier_agent.classify(book)