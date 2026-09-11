from bookmatch.models.book import BookInput, EnrichedBook
from bookmatch.models.book_candidate import BookCandidate
from bookmatch.models.book_resolution import (
    BookResolution,
    ResolutionDecision,
)
from bookmatch.services.book_identification_service import BookIdentificationService
from bookmatch.services.book_resolution_service import (
    BookResolutionService,
)

from bookmatch.services.book_resolution_service import (
    BookResolutionService,
    BookResolutionServiceImpl,
)

def make_book(
    title: str,
    author: str,
) -> EnrichedBook:
    return EnrichedBook(
        title=title,
        author=author,
        publication_date=None,
        isbn=None,
        description=None,
        source="Test",
    )

def test_book_resolution_service_is_abstract():
    assert BookResolutionService.__abstractmethods__ == {"resolve"}

def test_no_candidates_returns_not_found():
    service = BookResolutionServiceImpl(
        identification_service=BookIdentificationService(),
    )

    result = service.resolve(
        BookInput(title="Dog Man"),
        [],
    )

    assert result.decision == ResolutionDecision.NOT_FOUND
    assert result.selected_book is None
    assert result.candidates == []


def test_single_candidate_is_auto_resolved():
    book = make_book("Dog Man", "Dav Pilkey")

    service = BookResolutionServiceImpl(
        identification_service=BookIdentificationService(),
    )

    result = service.resolve(
        BookInput(title="Dog Man"),
        [
            BookCandidate(
                book=book,
                provider="Google Books",
            )
        ],
    )

    assert result.decision == ResolutionDecision.AUTO_RESOLVE
    assert result.selected_book == book
    assert result.candidates == []


def test_multiple_candidates_for_same_work_are_auto_resolved():
    first_book = make_book("Dog Man", "Dav Pilkey")
    second_book = make_book(
        "Dog Man: The Epic Collection",
        "Dav Pilkey",
    )

    service = BookResolutionServiceImpl(
        identification_service=BookIdentificationService(),
    )

    result = service.resolve(
        BookInput(title="Dog Man", author="Dav Pilkey"),
        [
            BookCandidate(
                book=first_book,
                provider="Google Books",
            ),
            BookCandidate(
                book=second_book,
                provider="Open Library",
            ),
        ],
    )

    assert result.decision == ResolutionDecision.AUTO_RESOLVE
    assert result.selected_book is not None
    assert result.candidates == []


def test_multiple_candidates_for_different_works_require_user_selection():
    first_book = make_book("Dog Man", "Dav Pilkey")
    second_book = make_book("Dog Man", "Maurice Procter")

    service = BookResolutionServiceImpl(
        identification_service=BookIdentificationService(),
    )

    result = service.resolve(
        BookInput(title="Dog Man"),
        [
            BookCandidate(
                book=first_book,
                provider="Google Books",
            ),
            BookCandidate(
                book=second_book,
                provider="Open Library",
            ),
        ],
    )

    assert result.decision == ResolutionDecision.ASK_USER
    assert result.selected_book is None
    assert result.candidates == [first_book, second_book]