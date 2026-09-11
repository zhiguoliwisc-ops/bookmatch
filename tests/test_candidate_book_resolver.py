from unittest.mock import Mock

import pytest

from bookmatch.models.book import BookInput, EnrichedBook
from bookmatch.models.book_candidate import BookCandidate
from bookmatch.models.book_resolution import (
    BookResolution,
    ResolutionDecision,
)
from bookmatch.services.book_candidate_service import (
    BookCandidateService,
)
from bookmatch.services.book_resolution_service import (
    BookResolutionService,
)
from bookmatch.services.candidate_book_resolver import (
    CandidateBookResolver,
)
from bookmatch.services.exceptions import (
    AmbiguousBookError,
    BookInformationServiceError,
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
    resolution_service = Mock(
        spec=BookResolutionService
    )

    candidate = create_candidate()

    candidate_service.find_candidates.return_value = [
        candidate
    ]

    resolution_service.resolve.return_value = BookResolution(
        decision=ResolutionDecision.AUTO_RESOLVE,
        selected_book=candidate.book,
    )

    resolver = CandidateBookResolver(
        candidate_service=candidate_service,
        resolution_service=resolution_service,
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

    resolution_service.resolve.assert_called_once_with(
        book,
        [candidate],
    )


def test_corrected_match_returns_enriched_book() -> None:
    candidate_service = Mock(spec=BookCandidateService)
    resolution_service = Mock(
        spec=BookResolutionService
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

    resolution_service.resolve.return_value = BookResolution(
        decision=ResolutionDecision.AUTO_RESOLVE,
        selected_book=candidate.book,
    )

    resolver = CandidateBookResolver(
        candidate_service=candidate_service,
        resolution_service=resolution_service,
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

    resolution_service.resolve.assert_called_once_with(
        book,
        [candidate],
    )


def test_not_found_raises_book_not_found_error() -> None:
    candidate_service = Mock(spec=BookCandidateService)
    resolution_service = Mock(
        spec=BookResolutionService
    )

    candidate_service.find_candidates.return_value = []

    resolution_service.resolve.return_value = BookResolution(
        decision=ResolutionDecision.NOT_FOUND,
    )

    resolver = CandidateBookResolver(
        candidate_service=candidate_service,
        resolution_service=resolution_service,
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

    resolution_service.resolve.assert_called_once_with(
        book,
        [],
    )


def test_ambiguous_match_raises_ambiguous_book_error() -> None:
    candidate_service = Mock(spec=BookCandidateService)
    resolution_service = Mock(
        spec=BookResolutionService
    )

    candidates = [
        create_candidate(
            title="Dog Man",
            author="Dav Pilkey",
        ),
        create_candidate(
            title="Dog Man",
            author="Maurice Procter",
        ),
    ]

    candidate_service.find_candidates.return_value = candidates

    resolution_service.resolve.return_value = BookResolution(
        decision=ResolutionDecision.ASK_USER,
        candidates=[
            candidate.book
            for candidate in candidates
        ],
    )

    resolver = CandidateBookResolver(
        candidate_service=candidate_service,
        resolution_service=resolution_service,
    )

    book = BookInput(
        title="Dog Man",
    )

    with pytest.raises(AmbiguousBookError) as error:
        resolver.resolve(book)

    assert error.value.candidates == [
        candidate.book
        for candidate in candidates
    ]

    candidate_service.find_candidates.assert_called_once_with(
        book
    )

    resolution_service.resolve.assert_called_once_with(
        book,
        candidates,
    )


def test_provider_failure_propagates_book_information_service_error() -> None:
    candidate_service = Mock(spec=BookCandidateService)
    resolution_service = Mock(
        spec=BookResolutionService
    )

    candidate_service.find_candidates.side_effect = (
        BookInformationServiceError(
            "All book information providers failed."
        )
    )

    resolver = CandidateBookResolver(
        candidate_service=candidate_service,
        resolution_service=resolution_service,
    )

    book = BookInput(
        title="Dog Man",
        author="Dav Pilkey",
    )

    with pytest.raises(BookInformationServiceError):
        resolver.resolve(book)

    candidate_service.find_candidates.assert_called_once_with(
        book
    )

    resolution_service.resolve.assert_not_called()