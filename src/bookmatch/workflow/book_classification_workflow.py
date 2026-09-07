from bookmatch.models.book import BookInput
from bookmatch.models.result import BookMatchResult
from bookmatch.services.book_information_service import (
    BookInformationService,
)
from bookmatch.services.classification_service import (
    ClassificationService,
)


class BookClassificationWorkflow:
    """Coordinate book information enrichment and classification."""

    def __init__(
        self,
        book_information_service: BookInformationService,
        classification_service: ClassificationService,
    ) -> None:
        self.book_information_service = book_information_service
        self.classification_service = classification_service

    def run(self, book: BookInput) -> BookMatchResult:
        """Enrich a book and classify it."""

        enriched_book = self.book_information_service.enrich(book)

        classification = self.classification_service.classify(
            enriched_book
        )

        return BookMatchResult(
            book=enriched_book,
            classification=classification,
        )