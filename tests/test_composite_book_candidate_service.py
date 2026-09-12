from unittest.mock import Mock

import pytest

from bookmatch.models.book import BookInput, EnrichedBook
from bookmatch.models.book_candidate import BookCandidate
from bookmatch.services.book_candidate_service import BookCandidateService
from bookmatch.services.composite_book_candidate_service import (
    CompositeBookCandidateService,
)
from bookmatch.services.exceptions import BookInformationServiceError


def create_candidate(
    title: str,
    author: str | None = None,
) -> BookCandidate:
    return BookCandidate(
        book=EnrichedBook(
            title=title,
            author=author,
            publication_date=None,
            isbn=None,
            description=None,
            source="Test",
        ),
        provider="Test",
    )


class FakeCandidateService(BookCandidateService):
    def __init__(
        self,
        candidates=None,
        error=None,
    ):
        self.candidates = candidates or []
        self.error = error
        self.calls = 0

    def find_candidates(self, book):
        self.calls += 1

        if self.error:
            raise self.error

        return self.candidates


def make_candidate(
    title: str = "Example Book",
    author: str = "E. B. White",
    isbn: str = "9780064400558",
) -> BookCandidate:
    return BookCandidate(
        book=EnrichedBook(
            title=title,
            author=author,
            publication_date="1952",
            isbn=isbn,
            description="A classic children's novel.",
            source="Test",
        ),
        provider="Test",
    )


def test_falls_back_when_first_service_returns_no_candidates():
    first = FakeCandidateService()

    second = FakeCandidateService(
        candidates=[
            make_candidate(
                title="Charlotte's Web",
                author="E. B. White",
            )
        ]
    )

    service = CompositeBookCandidateService([first, second])

    result = service.find_candidates(
        BookInput(title="Charlotte's Web")
    )

    assert result == second.candidates
    assert first.calls == 1
    assert second.calls == 1


def test_falls_back_when_first_service_has_provider_error():
    first = FakeCandidateService(
        error=BookInformationServiceError(
            "provider unavailable"
        )
    )

    second = FakeCandidateService(
        candidates=[
            make_candidate(
                title="Charlotte's Web",
                author="E. B. White",
            )
        ]
    )

    service = CompositeBookCandidateService([first, second])

    result = service.find_candidates(
        BookInput(title="Charlotte's Web")
    )

    assert result == second.candidates
    assert first.calls == 1
    assert second.calls == 1


def test_returns_empty_when_all_services_return_no_candidates():
    first = FakeCandidateService()
    second = FakeCandidateService()

    service = CompositeBookCandidateService([first, second])

    result = service.find_candidates(
        BookInput(title="Unknown Book")
    )

    assert result == []


def test_raises_when_no_candidate_services_are_configured():
    service = CompositeBookCandidateService([])

    with pytest.raises(ValueError):
        service.find_candidates(
            BookInput(title="Charlotte's Web")
        )


def test_does_not_swallow_unexpected_exceptions():
    first = FakeCandidateService(
        error=RuntimeError("unexpected bug")
    )

    second = FakeCandidateService(
        candidates=[
            make_candidate(
                title="Charlotte's Web",
                author="E. B. White",
            )
        ]
    )

    service = CompositeBookCandidateService([first, second])

    with pytest.raises(
        RuntimeError,
        match="unexpected bug",
    ):
        service.find_candidates(
            BookInput(title="Charlotte's Web")
        )

    assert first.calls == 1
    assert second.calls == 0


def test_combines_candidates_from_multiple_services():
    first_candidate = make_candidate(
        title="A Deadly Wandering",
        isbn="9781111111111",
    )

    second_candidate = make_candidate(
        title="A Deadly Wandering: A Mystery",
        isbn="9782222222222",
    )

    first = FakeCandidateService(
        candidates=[first_candidate]
    )

    second = FakeCandidateService(
        candidates=[second_candidate]
    )

    service = CompositeBookCandidateService([first, second])

    result = service.find_candidates(
        BookInput(title="A Deadly Wandering")
    )

    assert result == [
        first_candidate,
        second_candidate,
    ]

    assert first.calls == 1
    assert second.calls == 1


def test_deduplicates_candidates_from_multiple_services():
    first_candidate = make_candidate(
        title="Example Book",
        isbn="9781234567890",
    )

    second_candidate = make_candidate(
        title="Example Book",
        isbn="9781234567890",
    )

    first = FakeCandidateService(
        candidates=[first_candidate]
    )

    second = FakeCandidateService(
        candidates=[second_candidate]
    )

    service = CompositeBookCandidateService([first, second])

    result = service.find_candidates(
        BookInput(title="Example Book")
    )

    assert result == [first_candidate]
    assert first.calls == 1
    assert second.calls == 1


def test_raises_when_all_provider_services_fail() -> None:
    service1 = Mock()

    service1.find_candidates.side_effect = (
        BookInformationServiceError(
            "Google Books failed."
        )
    )

    service2 = Mock()

    service2.find_candidates.side_effect = (
        BookInformationServiceError(
            "Open Library failed."
        )
    )

    composite = CompositeBookCandidateService(
        services=[service1, service2]
    )

    with pytest.raises(BookInformationServiceError):
        composite.find_candidates(
            BookInput(title="Dog Man")
        )


def test_returns_candidates_when_one_provider_fails():
    failing_service = Mock()

    failing_service.find_candidates.side_effect = (
        BookInformationServiceError(
            "Google Books failed."
        )
    )

    working_service = Mock()

    working_service.find_candidates.return_value = [
        BookCandidate(
            book=EnrichedBook(
                title="Dog Man",
                author="Dav Pilkey",
                publication_date=None,
                isbn="9781338611941",
                description=None,
                source="Open Library",
            ),
            provider="Open Library",
        )
    ]

    composite = CompositeBookCandidateService(
        services=[
            failing_service,
            working_service,
        ]
    )

    candidates = composite.find_candidates(
        BookInput(title="Dog Man")
    )

    assert len(candidates) == 1
    assert candidates[0].book.title == "Dog Man"


def test_composite_candidate_service_ranks_candidates() -> None:
    book = BookInput(title="16 Forever")

    first_service = Mock()

    first_service.find_candidates.return_value = [
        create_candidate(
            "Node.js Recipes",
            "Cory Gackenheimer",
        ),
        create_candidate(
            "16 Forever",
            "Lance Rubin",
        ),
    ]

    second_service = Mock()

    second_service.find_candidates.return_value = [
        create_candidate(
            "Forever Strong",
            "Gabrielle Lyon",
        ),
    ]

    service = CompositeBookCandidateService(
        services=[
            first_service,
            second_service,
        ],
    )

    candidates = service.find_candidates(book)

    assert candidates[0].book.title == "16 Forever"
    assert candidates[1].book.title == "Forever Strong"
    assert len(candidates) == 2

def test_composite_candidate_service_limits_candidates_to_10() -> None:
    book = BookInput(title="Book")

    first_service = Mock()
    first_service.find_candidates.return_value = [
        create_candidate(
            f"Book {index}",
            f"Author {index}",
        )
        for index in range(1, 16)
    ]

    service = CompositeBookCandidateService(
        services=[first_service],
    )

    candidates = service.find_candidates(book)

    assert len(candidates) == 10
    assert [candidate.book.title for candidate in candidates] == [
        f"Book {index}"
        for index in range(1, 11)
    ]