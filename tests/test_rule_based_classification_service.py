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
    assert result.minimum_age == 3
    assert result.maximum_age == 5
    assert result.reading_difficulty == ReadingDifficulty.VERY_EASY
    assert result.genre == "Children's Fiction"
    assert result.confidence == 0.9


def test_classify_early_reader():
    service = RuleBasedClassificationService()

    book = BookInput(
        title="Example Early Reader",
        description="An early reader book about friendship and adventure.",
    )

    result = service.classify(book)

    assert result.recommended_age_group == AgeGroup.EARLY_ELEMENTARY
    assert result.minimum_age == 5
    assert result.maximum_age == 7
    assert result.reading_difficulty == ReadingDifficulty.EASY
    assert result.genre == "Children's Fiction"


def test_classify_young_adult_book():
    service = RuleBasedClassificationService()

    book = BookInput(
        title="Example YA Novel",
        description="A young adult novel about identity and growing up.",
    )

    result = service.classify(book)

    assert result.recommended_age_group == AgeGroup.HIGH_SCHOOL
    assert result.minimum_age == 14
    assert result.maximum_age == 18
    assert result.reading_difficulty == ReadingDifficulty.CHALLENGING
    assert result.genre == "Young Adult Fiction"


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