import pytest

from bookmatch.models.book import BookInput
from bookmatch.models.book_candidate import BookCandidate
from bookmatch.services.book_candidate_service import (
    BookCandidateService,
)


def test_book_candidate_service_requires_find_candidates() -> None:
    with pytest.raises(TypeError):
        BookCandidateService()


def test_concrete_candidate_service_can_be_created() -> None:
    class TestBookCandidateService(BookCandidateService):
        def find_candidates(
            self,
            book: BookInput,
        ) -> list[BookCandidate]:
            return []

    service = TestBookCandidateService()

    result = service.find_candidates(
        BookInput(title="A Wrinkle in Time")
    )

    assert result == []