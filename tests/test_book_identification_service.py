from bookmatch.models.book import BookInput, EnrichedBook
from bookmatch.models.book_candidate import BookCandidate
from bookmatch.models.book_identification import (
    IdentificationStatus,
)
from bookmatch.services.book_identification_service import (
    BookIdentificationService,
)


def create_candidate(
    title: str,
    author: str,
) -> BookCandidate:
    book = EnrichedBook(
        title=title,
        author=author,
        publication_date=None,
        isbn=None,
        description=None,
        source="Google Books",
    )

    return BookCandidate(
        book=book,
        provider="Google Books",
    )


def test_exact_title_and_author_match() -> None:
    service = BookIdentificationService()

    book = BookInput(
        title="A Wrinkle in Time",
        author="Madeline L'Engle",
    )

    candidate = create_candidate(
        "A Wrinkle in Time",
        "Madeline L'Engle",
    )

    result = service.identify(book, [candidate])

    assert result.status == IdentificationStatus.EXACT_MATCH
    assert result.matched_book == candidate.book
    assert result.confidence == 1.0


def test_title_with_extra_subtitle_is_corrected_match() -> None:
    service = BookIdentificationService()

    book = BookInput(
        title="A Deadly Wandering",
        author="Matt Richtel",
    )

    candidate = create_candidate(
        "A Deadly Wandering: A Mystery, A Landmark Investigation",
        "Matt Richtel",
    )

    result = service.identify(book, [candidate])

    assert result.status == IdentificationStatus.CORRECTED_MATCH
    assert result.matched_book == candidate.book
    assert result.confidence == 0.95


def test_title_matching_ignores_case_and_extra_whitespace() -> None:
    service = BookIdentificationService()

    book = BookInput(
        title="  A   Perfect Day ",
        author="Lane Smith",
    )

    candidate = create_candidate(
        "A Perfect Day",
        "Lane Smith",
    )

    result = service.identify(book, [candidate])

    assert result.status == IdentificationStatus.EXACT_MATCH


def test_author_mismatch_is_not_accepted() -> None:
    service = BookIdentificationService()

    book = BookInput(
        title="A Perfect Day",
        author="Different Author",
    )

    candidate = create_candidate(
        "A Perfect Day",
        "Lane Smith",
    )

    result = service.identify(book, [candidate])

    assert result.status == IdentificationStatus.NOT_FOUND
    assert result.matched_book is None


def test_multiple_matching_candidates_are_ambiguous() -> None:
    service = BookIdentificationService()

    book = BookInput(
        title="The Outsiders",
        author="S. E. Hinton",
    )

    candidates = [
        create_candidate(
            "The Outsiders",
            "S. E. Hinton",
        ),
        create_candidate(
            "The Outsiders",
            "S. E. Hinton",
        ),
    ]

    result = service.identify(book, candidates)

    assert result.status == IdentificationStatus.AMBIGUOUS
    assert result.matched_book is None


def test_no_candidates_returns_not_found() -> None:
    service = BookIdentificationService()

    book = BookInput(
        title="Unknown Book",
        author="Unknown Author",
    )

    result = service.identify(book, [])

    assert result.status == IdentificationStatus.NOT_FOUND
    assert result.matched_book is None


def test_unrelated_title_returns_not_found() -> None:
    service = BookIdentificationService()

    book = BookInput(
        title="A Wrinkle in Time",
        author="Madeleine L'Engle",
    )

    candidate = create_candidate(
        "The Great Gatsby",
        "F. Scott Fitzgerald",
    )

    result = service.identify(book, [candidate])

    assert result.status == IdentificationStatus.NOT_FOUND
    assert result.matched_book is None


def test_matching_isbn_returns_exact_match() -> None:
    service = BookIdentificationService()

    book = BookInput(
        title="Some Book",
        author="Some Author",
        isbn="978-1234567890",
    )

    candidate = create_candidate(
        "Completely Different Title",
        "Different Author",
    )

    candidate.book.isbn = "9781234567890"

    result = service.identify(book, [candidate])

    assert result.status == IdentificationStatus.EXACT_MATCH
    assert result.matched_book == candidate.book


def test_isbn_match_ignores_formatting() -> None:
    service = BookIdentificationService()

    book = BookInput(
        title="Some Book",
        isbn="978-123-4567890",
    )

    candidate = create_candidate(
        "Some Book",
        "Some Author",
    )

    candidate.book.isbn = "9781234567890"

    result = service.identify(book, [candidate])

    assert result.status == IdentificationStatus.EXACT_MATCH


def test_isbn_mismatch_does_not_fall_back_to_title() -> None:
    service = BookIdentificationService()

    book = BookInput(
        title="Some Book",
        author="Some Author",
        isbn="9781234567890",
    )

    candidate = create_candidate(
        "Some Book",
        "Some Author",
    )

    candidate.book.isbn = "9780987654321"

    result = service.identify(book, [candidate])

    assert result.status == IdentificationStatus.NOT_FOUND
    assert result.matched_book is None


def test_isbn_without_candidate_is_not_found() -> None:
    service = BookIdentificationService()

    book = BookInput(
        title="Some Book",
        author="Some Author",
        isbn="9781234567890",
    )

    candidate = create_candidate(
        "Some Book",
        "Some Author",
    )

    result = service.identify(book, [candidate])

    assert result.status == IdentificationStatus.NOT_FOUND
    assert result.matched_book is None