import pytest

from bookmatch.models.book import BookInput, EnrichedBook
from bookmatch.models.book_candidate import BookCandidate
from bookmatch.services.book_candidate_service import BookCandidateService
from bookmatch.services.exceptions import BookInformationServiceError

class FakeCandidateService(BookCandidateService):
    def __init__(self, candidates=None, error=None):
        self.candidates = candidates or []
        self.error = error
        self.calls = 0

    def find_candidates(self, book):
        self.calls += 1
        if self.error:
            raise self.error
        return self.candidates


def make_candidate(title="Charlotte's Web"):
    return BookCandidate(
        book=EnrichedBook(
            title=title,
            author="E. B. White",
            publication_date="1952",
            isbn="9780064400558",
            description="A classic children's novel.",
            source="Test",
        ),
        provider="Test",
    )


def test_returns_candidates_from_first_service():
    first = FakeCandidateService(
        candidates=[make_candidate()]
    )
    second = FakeCandidateService(
        candidates=[make_candidate("Other Book")]
    )

    # This import should fail initially.
    from bookmatch.services.composite_book_candidate_service import (
        CompositeBookCandidateService,
    )

    service = CompositeBookCandidateService([first, second])

    result = service.find_candidates(
        BookInput(title="Charlotte's Web")
    )

    assert result == first.candidates
    assert first.calls == 1
    assert second.calls == 0


def test_falls_back_when_first_service_returns_no_candidates():
    first = FakeCandidateService()
    second = FakeCandidateService(
        candidates=[make_candidate()]
    )

    from bookmatch.services.composite_book_candidate_service import (
        CompositeBookCandidateService,
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
        error=BookInformationServiceError("provider unavailable")
    )
    second = FakeCandidateService(
        candidates=[make_candidate()]
    )

    from bookmatch.services.composite_book_candidate_service import (
        CompositeBookCandidateService,
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

    from bookmatch.services.composite_book_candidate_service import (
        CompositeBookCandidateService,
    )

    service = CompositeBookCandidateService([first, second])

    result = service.find_candidates(
        BookInput(title="Unknown Book")
    )

    assert result == []


def test_raises_when_no_candidate_services_are_configured():
    from bookmatch.services.composite_book_candidate_service import (
        CompositeBookCandidateService,
    )

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
        candidates=[make_candidate()]
    )

    from bookmatch.services.composite_book_candidate_service import (
        CompositeBookCandidateService,
    )

    service = CompositeBookCandidateService([first, second])

    with pytest.raises(RuntimeError, match="unexpected bug"):
        service.find_candidates(
            BookInput(title="Charlotte's Web")
        )

    assert first.calls == 1
    assert second.calls == 0