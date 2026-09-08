from bookmatch.models.book import EnrichedBook
from bookmatch.models.book_candidate import BookCandidate


def create_book() -> EnrichedBook:
    return EnrichedBook(
        title="A Wrinkle in Time",
        author="Madeleine L'Engle",
        publication_date=None,
        isbn="9780312367541",
        description=None,
        source="Google Books",
    )


def test_book_candidate_contains_book_and_provider() -> None:
    book = create_book()

    candidate = BookCandidate(
        book=book,
        provider="Google Books",
    )

    assert candidate.book == book
    assert candidate.provider == "Google Books"


def test_book_candidate_can_use_open_library() -> None:
    book = create_book()

    candidate = BookCandidate(
        book=book,
        provider="Open Library",
    )

    assert candidate.provider == "Open Library"