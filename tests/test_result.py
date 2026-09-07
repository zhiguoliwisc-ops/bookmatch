from bookmatch.models.book import EnrichedBook
from bookmatch.models.classification import (
    AgeGroup,
    BookClassification,
    ReadingDifficulty,
)
from bookmatch.models.result import BookMatchResult


def test_create_book_match_result():
    book = EnrichedBook(
        title="Charlotte's Web",
        author="E. B. White",
        publication_date="1952",
        isbn="9780064400558",
        description="A children's novel about a pig and a spider.",
        source="Test",
    )

    classification = BookClassification(
        recommended_age_group=AgeGroup.ELEMENTARY,
        minimum_age=7,
        maximum_age=10,
        reading_difficulty=ReadingDifficulty.MODERATE,
        genre="Children's Fiction",
        confidence=0.9,
    )

    result = BookMatchResult(
        book=book,
        classification=classification,
    )

    assert result.book.title == "Charlotte's Web"
    assert result.book.author == "E. B. White"
    assert result.classification.recommended_age_group == AgeGroup.ELEMENTARY
    assert result.classification.minimum_age == 7
    assert result.classification.maximum_age == 10
    assert result.classification.reading_difficulty == ReadingDifficulty.MODERATE
    assert result.classification.genre == "Children's Fiction"