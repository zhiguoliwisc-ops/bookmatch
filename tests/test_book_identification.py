from bookmatch.models.book import EnrichedBook
from bookmatch.models.book_identification import (
    BookIdentification,
    IdentificationStatus,
)


def create_book() -> EnrichedBook:
    return EnrichedBook(
        title="A Deadly Wandering: A Mystery",
        author="Matt Richtel",
        publication_date=None,
        isbn=None,
        description=None,
        source="Google Books",
    )


def test_exact_match() -> None:
    result = BookIdentification(
        status=IdentificationStatus.EXACT_MATCH,
        matched_book=create_book(),
        confidence=1.0,
        reason="Title and author match the input.",
    )

    assert result.status == IdentificationStatus.EXACT_MATCH
    assert result.matched_book is not None
    assert result.confidence == 1.0


def test_corrected_match() -> None:
    result = BookIdentification(
        status=IdentificationStatus.CORRECTED_MATCH,
        matched_book=create_book(),
        confidence=0.95,
        reason=(
            "Input title matched a longer canonical title "
            "with the same author."
        ),
    )

    assert result.status == IdentificationStatus.CORRECTED_MATCH
    assert result.matched_book is not None


def test_ambiguous_match() -> None:
    result = BookIdentification(
        status=IdentificationStatus.AMBIGUOUS,
        matched_book=None,
        confidence=0.5,
        reason=(
            "Multiple books match the title, but the available "
            "metadata does not uniquely identify one."
        ),
    )

    assert result.status == IdentificationStatus.AMBIGUOUS
    assert result.matched_book is None


def test_not_found() -> None:
    result = BookIdentification(
        status=IdentificationStatus.NOT_FOUND,
        matched_book=None,
        confidence=0.0,
        reason="No sufficiently matching candidate was found.",
    )

    assert result.status == IdentificationStatus.NOT_FOUND
    assert result.matched_book is None


def test_confidence_must_be_between_zero_and_one() -> None:
    try:
        BookIdentification(
            status=IdentificationStatus.NOT_FOUND,
            matched_book=None,
            confidence=1.5,
            reason="Invalid confidence.",
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for invalid confidence."
        )