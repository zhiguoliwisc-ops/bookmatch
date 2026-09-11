from bookmatch.models.book import BookInput, EnrichedBook
from bookmatch.models.classification import BookClassification
from bookmatch.models.result import BookMatchResult
from bookmatch.services.book_classifier_agent import (
    BookClassifierAgent,
)
from bookmatch.services.book_resolver import BookResolver
from bookmatch.services.book_reviewer_agent import (
    BookReviewerAgent,
)
from bookmatch.models.classification_review import ClassificationReview

class BookClassificationWorkflow:
    """Coordinate book resolution, classification, and review."""

    def __init__(
        self,
        book_resolver: BookResolver,
        classifier_agent: BookClassifierAgent,
        reviewer_agent: BookReviewerAgent,
    ) -> None:
        self.book_resolver = book_resolver
        self.classifier_agent = classifier_agent
        self.reviewer_agent = reviewer_agent

    def run(self, book: BookInput) -> BookMatchResult:
        """Resolve a book, classify it, and review the classification."""

        enriched_book = self.book_resolver.resolve(book)

        classification = self.classifier_agent.classify(
            enriched_book
        )

        review = self.reviewer_agent.review(
            enriched_book,
            classification,
        )

        return BookMatchResult(
            book=enriched_book,
            classification=classification,
            review=review,
        )

    def classify_book(
        self,
        book: EnrichedBook,
    ) -> BookClassification:
        """Classify an already resolved book."""
        return self.classifier_agent.classify(book)

    def review_book(
        self,
        book: EnrichedBook,
        classification: BookClassification,
    ) -> ClassificationReview:
        """Review a classification for an already resolved book."""
        return self.reviewer_agent.review(
            book,
            classification,
        )