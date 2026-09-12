from bookmatch.models.book import EnrichedBook
from bookmatch.services.candidate_display_deduplication import (
    deduplicate_display_candidates,
)


def create_book(
    title: str,
    author: str | None = None,
    isbn: str | None = None,
) -> EnrichedBook:
    return EnrichedBook(
        title=title,
        author=author,
        publication_date=None,
        isbn=isbn,
        description=None,
        source="Test",
    )


def test_removes_duplicate_display_candidates_with_same_title_and_author() -> None:
    first = create_book(
        title="16 Forever",
        author="Lance Rubin",
        isbn="9780000000001",
    )

    second = create_book(
        title="16 Forever",
        author="Lance Rubin",
        isbn="9780000000002",
    )

    result = deduplicate_display_candidates(
        [first, second]
    )

    assert result == [first]


def test_keeps_display_candidates_with_different_authors() -> None:
    first = create_book(
        title="Dog Man",
        author="Dav Pilkey",
        isbn="9780000000001",
    )

    second = create_book(
        title="Dog Man",
        author="Maurice Procter",
        isbn="9780000000002",
    )

    result = deduplicate_display_candidates(
        [first, second]
    )

    assert result == [first, second]


def test_keeps_display_candidates_with_different_titles() -> None:
    first = create_book(
        title="16 Forever",
        author="Lance Rubin",
    )

    second = create_book(
        title="16 Steps to Forever",
        author="Georgia Beers",
    )

    result = deduplicate_display_candidates(
        [first, second]
    )

    assert result == [first, second]


def test_preserves_first_candidate_when_duplicates_are_found() -> None:
    first = create_book(
        title="16 Forever",
        author="Lance Rubin",
        isbn="9780000000001",
    )

    second = create_book(
        title=" 16   FOREVER ",
        author=" lance rubin ",
        isbn="9780000000002",
    )

    result = deduplicate_display_candidates(
        [first, second]
    )

    assert result == [first]