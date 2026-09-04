import pytest

from bookmatch.models.book import BookInput
from bookmatch.models.classification import (
    AgeGroup,
    ReadingDifficulty,
)
from bookmatch.services.exceptions import InsufficientBookInformationError
from bookmatch.services.rule_based_classification_service import (
    RuleBasedClassificationService,
)


def test_classify_picture_book():
    service = RuleBasedClassificationService()

    book = BookInput(
        title="Example Picture Book",
        description="A beautifully illustrated picture book for young children.",
    )

    result = service.classify(book)

    assert result.recommended_age_group == AgeGroup.PRESCHOOL
    assert result.reading_difficulty == ReadingDifficulty.VERY_EASY
    assert result.confidence == 0.9


def test_classify_early_reader():
    service = RuleBasedClassificationService()

    book = BookInput(
        title="Example Early Reader",
        description="An early reader book about friendship and adventure.",
    )

    result = service.classify(book)

    assert result.recommended_age_group == AgeGroup.EARLY_ELEMENTARY
    assert result.reading_difficulty == ReadingDifficulty.EASY


def test_classify_young_adult_book():
    service = RuleBasedClassificationService()

    book = BookInput(
        title="Example YA Novel",
        description="A young adult novel about identity and growing up.",
    )

    result = service.classify(book)

    assert result.recommended_age_group == AgeGroup.HIGH_SCHOOL
    assert result.reading_difficulty == ReadingDifficulty.CHALLENGING


def test_raise_error_when_description_is_missing():
    service = RuleBasedClassificationService()

    book = BookInput(
        title="Unknown Book",
    )

    with pytest.raises(InsufficientBookInformationError):
        service.classify(book)


def test_raise_error_when_description_has_no_known_signal():
    service = RuleBasedClassificationService()

    book = BookInput(
        title="Unknown Book",
        description="This is a book with no recognizable classification signal.",
    )

    with pytest.raises(InsufficientBookInformationError):
        service.classify(book)