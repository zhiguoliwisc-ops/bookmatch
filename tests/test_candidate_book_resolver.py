from unittest.mock import Mock

import pytest

from bookmatch.models.book import BookInput, EnrichedBook
from bookmatch.models.book_candidate import BookCandidate
from bookmatch.models.book_identification import (
    BookIdentification,
    IdentificationStatus,
)
from bookmatch.services.book_candidate_service import (
    BookCandidateService,
)
from bookmatch.services.book_identification_service import (
    BookIdentificationService,
)
from bookmatch.services.candidate_book_resolver import (
    CandidateBookResolver,
)
from bookmatch.services.exceptions import (
    AmbiguousBookError,
    BookNotFoundError,
)


def create_candidate(
    title: str = "A Wrinkle in Time",
    author: str = "Madeleine L'Engle",
) -> BookCandidate:
    book = EnrichedBook(
        title=title,
        author=author,
        publication_date="1962",
        isbn="9780312367541",
        description="A science fiction novel.",
        source="Google Books",
    )

    return BookCandidate(
        book=book,
        provider="Google Books",
    )


def test_exact_match_returns_enriched_book() -> None:
    candidate_service = Mock(spec=BookCandidateService)
    identification_service = Mock(
        spec=BookIdentificationService
    )

    candidate = create_candidate()

    candidate_service.find_candidates.return_value = [
        candidate
    ]

    identification_service.identify.return_value = (
        BookIdentification(
            status=IdentificationStatus.EXACT_MATCH,
            matched_book=candidate.book,
            confidence=1.0,
            reason="Title and author match the input.",
        )
    )

    resolver = CandidateBookResolver(
        candidate_service=candidate_service,
        identification_service=identification_service,
    )

    book = BookInput(
        title="A Wrinkle in Time",
        author="Madeleine L'Engle",
    )

    result = resolver.resolve(book)

    assert result == candidate.book

    candidate_service.find_candidates.assert_called_once_with(
        book
    )

    identification_service.identify.assert_called_once_with(
        book,
        [candidate],
    )


def test_corrected_match_returns_enriched_book() -> None:
    candidate_service = Mock(spec=BookCandidateService)
    identification_service = Mock(
        spec=BookIdentificationService
    )

    candidate = create_candidate(
        title=(
            "A Deadly Wandering: A Mystery, "
            "A Landmark Investigation"
        ),
        author="Matt Richtel",
    )

    candidate_service.find_candidates.return_value = [
        candidate
    ]

    identification_service.identify.return_value = (
        BookIdentification(
            status=IdentificationStatus.CORRECTED_MATCH,
            matched_book=candidate.book,
            confidence=0.95,
            reason=(
                "Input title matched a longer canonical "
                "title with the same author."
            ),
        )
    )

    resolver = CandidateBookResolver(
        candidate_service=candidate_service,
        identification_service=identification_service,
    )

    book = BookInput(
        title="A Deadly Wandering",
        author="Matt Richtel",
    )

    result = resolver.resolve(book)

    assert result == candidate.book

    candidate_service.find_candidates.assert_called_once_with(
        book
    )

    identification_service.identify.assert_called_once_with(
        book,
        [candidate],
    )


def test_not_found_raises_book_not_found_error() -> None:
    candidate_service = Mock(spec=BookCandidateService)
    identification_service = Mock(
        spec=BookIdentificationService
    )

    candidate_service.find_candidates.return_value = []

    identification_service.identify.return_value = (
        BookIdentification(
            status=IdentificationStatus.NOT_FOUND,
            matched_book=None,
            confidence=0.0,
            reason="No candidate books were found.",
        )
    )

    resolver = CandidateBookResolver(
        candidate_service=candidate_service,
        identification_service=identification_service,
    )

    book = BookInput(
        title="Unknown Book",
        author="Unknown Author",
    )

    with pytest.raises(BookNotFoundError):
        resolver.resolve(book)

    candidate_service.find_candidates.assert_called_once_with(
        book
    )

    identification_service.identify.assert_called_once_with(
        book,
        [],
    )


def test_ambiguous_match_raises_ambiguous_book_error() -> None:
    candidate_service = Mock(spec=BookCandidateService)
    identification_service = Mock(
        spec=BookIdentificationService
    )

    candidates = [
        create_candidate(),
        create_candidate(),
    ]

    candidate_service.find_candidates.return_value = candidates

    identification_service.identify.return_value = (
        BookIdentification(
            status=IdentificationStatus.AMBIGUOUS,
            matched_book=None,
            confidence=0.5,
            reason=(
                "Multiple candidates match the title "
                "and author."
            ),
        )
    )

    resolver = CandidateBookResolver(
        candidate_service=candidate_service,
        identification_service=identification_service,
    )

    book = BookInput(
        title="The Outsiders",
        author="S. E. Hinton",
    )

    with pytest.raises(AmbiguousBookError):
        resolver.resolve(book)

    candidate_service.find_candidates.assert_called_once_with(
        book
    )

    identification_service.identify.assert_called_once_with(
        book,
        candidates,
    )