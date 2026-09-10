from bookmatch.models.book import EnrichedBook
from bookmatch.models.book_candidate import BookCandidate
from bookmatch.services.candidate_deduplication import (
    deduplicate_candidates,
)


def make_candidate(
    title: str,
    author: str | None = "Test Author",
    isbn: str | None = None,
    provider: str = "Test Provider",
) -> BookCandidate:
    return BookCandidate(
        book=EnrichedBook(
            title=title,
            author=author,
            publication_date=None,
            isbn=isbn,
            description=None,
            source=provider,
        ),
        provider=provider,
    )


def test_removes_candidates_with_same_isbn():
    first = make_candidate(
        title="Example Book",
        isbn="9781234567890",
        provider="Google Books",
    )
    second = make_candidate(
        title="Example Book",
        isbn="9781234567890",
        provider="Open Library",
    )

    result = deduplicate_candidates([first, second])

    assert result == [first]


def test_removes_candidates_with_same_title_and_author_when_isbn_missing():
    first = make_candidate(
        title="Example Book",
        author="Test Author",
        provider="Google Books",
    )
    second = make_candidate(
        title="Example Book",
        author="Test Author",
        provider="Open Library",
    )

    result = deduplicate_candidates([first, second])

    assert result == [first]


def test_keeps_candidates_with_different_isbn():
    first = make_candidate(
        title="Example Book",
        isbn="9781234567890",
    )
    second = make_candidate(
        title="Example Book",
        isbn="9780987654321",
    )

    result = deduplicate_candidates([first, second])

    assert result == [first, second]


def test_keeps_candidates_with_different_authors():
    first = make_candidate(
        title="Example Book",
        author="Author One",
    )
    second = make_candidate(
        title="Example Book",
        author="Author Two",
    )

    result = deduplicate_candidates([first, second])

    assert result == [first, second]


def test_title_and_author_matching_is_case_insensitive():
    first = make_candidate(
        title="Example Book",
        author="Test Author",
    )
    second = make_candidate(
        title=" example   book ",
        author="test author",
    )

    result = deduplicate_candidates([first, second])

    assert result == [first]


def test_does_not_merge_different_books_with_same_author():
    first = make_candidate(
        title="Book One",
        author="Test Author",
    )
    second = make_candidate(
        title="Book Two",
        author="Test Author",
    )

    result = deduplicate_candidates([first, second])

    assert result == [first, second]

def test_removes_duplicate_when_one_candidate_has_no_isbn():
    first = make_candidate(
        title="Example Book",
        author="Test Author",
        isbn="9781234567890",
        provider="Google Books",
    )
    second = make_candidate(
        title="Example Book",
        author="Test Author",
        isbn=None,
        provider="Open Library",
    )

    result = deduplicate_candidates([first, second])

    assert result == [first]