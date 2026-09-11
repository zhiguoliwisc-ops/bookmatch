from unittest.mock import Mock

import pytest

from bookmatch.models.book import BookInput, EnrichedBook
from bookmatch.models.classification import (
    AgeGroup,
    BookClassification,
    ReadingDifficulty,
)
from bookmatch.models.result import BookMatchResult
from bookmatch.services.book_classifier_agent import (
    BookClassifierAgent,
)
from bookmatch.services.book_resolver import BookResolver
from bookmatch.services.classification_service import (
    ClassificationService,
)
from bookmatch.services.exceptions import (
    BookInformationServiceError,
)
from bookmatch.workflow.book_classification_workflow import (
    BookClassificationWorkflow,
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
    def classify(
        self,
        book: EnrichedBook,
    ) -> BookClassification:
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
        classifier_agent=classification_service,
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
        classifier_agent=classification_service,
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
        classifier_agent=classification_service,
    )

    book = BookInput(
        title="Dog Man",
        author="Dav Pilkey",
    )

    with pytest.raises(BookInformationServiceError):
        workflow.run(book)


def test_classify_book_classifies_already_resolved_book() -> None:
    book_resolver = Mock(spec=BookResolver)
    classification_service = Mock(
        spec=ClassificationService
    )

    enriched_book = EnrichedBook(
        title="Dog Man",
        author="Dav Pilkey",
        publication_date="2016",
        isbn="1338611941",
        description="A graphic novel about Dog Man.",
        source="Google Books",
    )

    classification = BookClassification(
        recommended_age_group=AgeGroup.ELEMENTARY,
        minimum_age=6,
        maximum_age=10,
        reading_difficulty=ReadingDifficulty.EASY,
        genre="Graphic Novel",
        confidence=0.95,
    )

    classification_service.classify.return_value = classification

    workflow = BookClassificationWorkflow(
        book_resolver=book_resolver,
        classifier_agent=classification_service,
    )

    result = workflow.classify_book(enriched_book)

    assert result == classification

    classification_service.classify.assert_called_once_with(
        enriched_book
    )

    book_resolver.resolve.assert_not_called()


def test_workflow_accepts_book_classifier_agent() -> None:
    book_resolver = Mock(spec=BookResolver)
    classifier_agent = Mock(spec=BookClassifierAgent)

    enriched_book = EnrichedBook(
        title="Dog Man",
        author="Dav Pilkey",
        publication_date="2016",
        isbn="1338611941",
        description="A graphic novel about Dog Man.",
        source="Google Books",
    )

    classification = BookClassification(
        recommended_age_group=AgeGroup.ELEMENTARY,
        minimum_age=6,
        maximum_age=10,
        reading_difficulty=ReadingDifficulty.EASY,
        genre="Graphic Novel",
        confidence=0.95,
    )

    book_resolver.resolve.return_value = enriched_book
    classifier_agent.classify.return_value = classification

    workflow = BookClassificationWorkflow(
        book_resolver=book_resolver,
        classifier_agent=classifier_agent,
    )

    result = workflow.run(
        BookInput(
            title="Dog Man",
            author="Dav Pilkey",
        )
    )

    assert result.classification == classification

    classifier_agent.classify.assert_called_once_with(
        enriched_book
    )