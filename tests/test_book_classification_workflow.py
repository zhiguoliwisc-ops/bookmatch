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
            reading_difficulty=ReadingDifficulty.VERY_EASY,
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

    assert result.recommended_age_group == AgeGroup.PRESCHOOL
    assert result.reading_difficulty == ReadingDifficulty.VERY_EASY
    assert result.confidence == 0.95