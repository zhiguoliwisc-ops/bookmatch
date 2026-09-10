from bookmatch.models.book import BookInput, EnrichedBook
from bookmatch.models.classification import (
    AgeGroup,
    BookClassification,
    ReadingDifficulty,
)
from bookmatch.services.book_resolver import BookResolver
from bookmatch.services.classification_service import (
    ClassificationService,
)
from bookmatch.workflow.book_classification_workflow import (
    BookClassificationWorkflow,
)

import pytest

from bookmatch.services.exceptions import (
    BookInformationServiceError,
)

class FakeBookResolver(BookResolver):
    def resolve(self, book: BookInput) -> EnrichedBook:
        return EnrichedBook(
            title=book.title,
            author=book.author,
            publication_date=book.publication_date,
            isbn=book.isbn,
            description="A picture book for young children.",
            source="Fake",
        )

class FailingBookResolver(BookResolver):
    def resolve(self, book: BookInput) -> EnrichedBook:
        raise BookInformationServiceError(
            "All book information providers failed."
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
    book_resolver = FakeBookResolver()
    classification_service = FakeClassificationService()

    workflow = BookClassificationWorkflow(
        book_resolver=book_resolver,
        classification_service=classification_service,
    )

    book = BookInput(
        title="Example Book",
        author="Example Author",
    )

    result = workflow.run(book)

    assert result.book.title == "Example Book"
    assert result.book.author == "Example Author"

    assert (
        result.classification.recommended_age_group
        == AgeGroup.PRESCHOOL
    )
    assert result.classification.minimum_age == 3
    assert result.classification.maximum_age == 5
    assert (
        result.classification.reading_difficulty
        == ReadingDifficulty.VERY_EASY
    )
    assert result.classification.genre == "Children's Fiction"
    assert result.classification.confidence == 0.95


def test_workflow_uses_book_resolver():
    book_resolver = FakeBookResolver()
    classification_service = FakeClassificationService()

    workflow = BookClassificationWorkflow(
        book_resolver=book_resolver,
        classification_service=classification_service,
    )

    book = BookInput(
        title="Charlotte's Web",
        author="E. B. White",
        isbn="9780064400558",
    )

    result = workflow.run(book)

    assert result.book.source == "Fake"
    assert result.book.title == "Charlotte's Web"
    assert result.book.author == "E. B. White"

def test_workflow_propagates_book_information_service_error():
    book_resolver = FailingBookResolver()
    classification_service = FakeClassificationService()

    workflow = BookClassificationWorkflow(
        book_resolver=book_resolver,
        classification_service=classification_service,
    )

    book = BookInput(
        title="Dog Man",
        author="Dav Pilkey",
    )

    with pytest.raises(BookInformationServiceError):
        workflow.run(book)