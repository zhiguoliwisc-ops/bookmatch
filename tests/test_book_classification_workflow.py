from bookmatch.models.book import BookInput, EnrichedBook
from bookmatch.models.classification import (
    AgeGroup,
    BookClassification,
    ReadingDifficulty,
)
from bookmatch.services.book_information_service import (
    BookInformationService,
)
from bookmatch.services.classification_service import (
    ClassificationService,
)
from bookmatch.workflow.book_classification_workflow import (
    BookClassificationWorkflow,
)
from unittest.mock import Mock
from bookmatch.services.cached_book_information_service import (
    CachedBookInformationService,
)

class FakeBookInformationService(BookInformationService):
    def enrich(self, book: BookInput) -> EnrichedBook:
        return EnrichedBook(
            title=book.title,
            author=book.author,
            publication_date=book.publication_date,
            isbn=book.isbn,
            description="A picture book for young children.",
            source="Fake",
        )


class FakeClassificationService(ClassificationService):
    def classify(self, book: BookInput) -> BookClassification:
        return BookClassification(
            recommended_age_group=AgeGroup.PRESCHOOL,
            minimum_age=3,
            maximum_age=5,
            reading_difficulty=ReadingDifficulty.VERY_EASY,
            genre="Children's Fiction",
            confidence=0.95,
        )


def test_book_classification_workflow():
    book_information_service = FakeBookInformationService()
    classification_service = FakeClassificationService()

    workflow = BookClassificationWorkflow(
        book_information_service=book_information_service,
        classification_service=classification_service,
    )

    book = BookInput(
        title="Example Book",
        author="Example Author",
    )

    result = workflow.run(book)

    assert result.book.title == "Example Book"
    assert result.book.author == "Example Author"

    assert result.classification.recommended_age_group == AgeGroup.PRESCHOOL
    assert result.classification.minimum_age == 3
    assert result.classification.maximum_age == 5
    assert result.classification.reading_difficulty == ReadingDifficulty.VERY_EASY
    assert result.classification.genre == "Children's Fiction"
    assert result.classification.confidence == 0.95

def test_workflow_uses_cached_book_information() -> None:
    book_information_service = Mock()

    enriched_book = EnrichedBook(
        title="Charlotte's Web",
        author="E. B. White",
        publication_date="1952",
        isbn="9780064400558",
        description="A story about a pig and a spider.",
        source="Google Books",
    )

    book_information_service.enrich.return_value = enriched_book

    cached_book_information_service = CachedBookInformationService(
        book_information_service,
    )

    classification_service = Mock()

    classification = BookClassification(
        recommended_age_group=AgeGroup.ELEMENTARY,
        minimum_age=6,
        maximum_age=10,
        reading_difficulty=ReadingDifficulty.MODERATE,
        genre="Fiction",
        confidence=0.9,
    )

    classification_service.classify.return_value = classification

    workflow = BookClassificationWorkflow(
        cached_book_information_service,
        classification_service,
    )

    book = BookInput(
        title="Charlotte's Web",
        author="E. B. White",
        isbn="9780064400558",
    )

    first_result = workflow.run(book)
    second_result = workflow.run(book)

    assert first_result.book == enriched_book
    assert second_result.book == enriched_book

    assert book_information_service.enrich.call_count == 1
    assert classification_service.classify.call_count == 2

