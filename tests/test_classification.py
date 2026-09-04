from bookmatch.models.classification import (
    AgeGroup,
    BookClassification,
    ReadingDifficulty,
)


def test_create_book_classification():
    classification = BookClassification(
        recommended_age_group=AgeGroup.ELEMENTARY,
        reading_difficulty=ReadingDifficulty.MODERATE,
        confidence=0.85,
    )

    assert classification.recommended_age_group == AgeGroup.ELEMENTARY
    assert classification.reading_difficulty == ReadingDifficulty.MODERATE
    assert classification.confidence == 0.85


def test_age_group_is_an_enum():
    classification = BookClassification(
        recommended_age_group=AgeGroup.MIDDLE_SCHOOL,
        reading_difficulty=ReadingDifficulty.CHALLENGING,
        confidence=0.9,
    )

    assert classification.recommended_age_group.value == "Middle School"


def test_reading_difficulty_is_an_enum():
    classification = BookClassification(
        recommended_age_group=AgeGroup.ADULT,
        reading_difficulty=ReadingDifficulty.ADVANCED,
        confidence=0.95,
    )

    assert classification.reading_difficulty.value == 5


def test_confidence_is_excluded_from_output():
    classification = BookClassification(
        recommended_age_group=AgeGroup.ELEMENTARY,
        reading_difficulty=ReadingDifficulty.MODERATE,
        confidence=0.85,
    )

    assert classification.confidence == 0.85

    output = classification.model_dump()

    assert "confidence" not in output