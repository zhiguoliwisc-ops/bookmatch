from bookmatch.models.classification import (
    AgeGroup,
    BookClassification,
    ReadingDifficulty,
)


def test_create_book_classification():
    classification = BookClassification(
        recommended_age_group=AgeGroup.ELEMENTARY,
        minimum_age=7,
        maximum_age=10,
        reading_difficulty=ReadingDifficulty.MODERATE,
        genre="Children's Fiction",
        confidence=0.85,
    )

    assert classification.recommended_age_group == AgeGroup.ELEMENTARY
    assert classification.minimum_age == 7
    assert classification.maximum_age == 10
    assert classification.reading_difficulty == ReadingDifficulty.MODERATE
    assert classification.genre == "Children's Fiction"
    assert classification.confidence == 0.85


def test_age_group_is_an_enum():
    classification = BookClassification(
        recommended_age_group=AgeGroup.MIDDLE_SCHOOL,
        minimum_age=11,
        maximum_age=13,
        reading_difficulty=ReadingDifficulty.CHALLENGING,
        genre="Middle Grade Fiction",
        confidence=0.9,
    )

    assert classification.recommended_age_group.value == "Middle School"


def test_reading_difficulty_is_an_enum():
    classification = BookClassification(
        recommended_age_group=AgeGroup.ADULT,
        minimum_age=18,
        maximum_age=99,
        reading_difficulty=ReadingDifficulty.ADVANCED,
        genre="Fiction",
        confidence=0.95,
    )

    assert classification.reading_difficulty.value == 5


def test_confidence_is_excluded_from_output():
    classification = BookClassification(
        recommended_age_group=AgeGroup.ELEMENTARY,
        minimum_age=7,
        maximum_age=10,
        reading_difficulty=ReadingDifficulty.MODERATE,
        genre="Children's Fiction",
        confidence=0.85,
    )

    assert classification.confidence == 0.85

    output = classification.model_dump()

    assert "confidence" not in output