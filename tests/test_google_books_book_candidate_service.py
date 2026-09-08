import httpx
import pytest

from bookmatch.models.book import BookInput
from bookmatch.models.book_candidate import BookCandidate
from bookmatch.services.exceptions import (
    BookInformationServiceError,
)
from bookmatch.services.google_books_book_candidate_service import (
    GoogleBooksBookCandidateService,
)


def test_build_query_with_title_and_author() -> None:
    book = BookInput(
        title="A Wrinkle in Time",
        author="Madeleine L'Engle",
    )

    query = (
        GoogleBooksBookCandidateService
        ._build_query(book)
    )

    assert query == (
        'intitle:"A Wrinkle in Time"'
        '+inauthor:"Madeleine L\'Engle"'
    )


def test_build_query_with_title_only() -> None:
    book = BookInput(
        title="A Wrinkle in Time",
    )

    query = (
        GoogleBooksBookCandidateService
        ._build_query(book)
    )

    assert query == 'intitle:"A Wrinkle in Time"'


def test_create_candidates() -> None:
    data = {
        "items": [
            {
                "volumeInfo": {
                    "title": "A Wrinkle in Time",
                    "authors": [
                        "Madeleine L'Engle"
                    ],
                    "publishedDate": "1962",
                    "industryIdentifiers": [
                        {
                            "type": "ISBN_13",
                            "identifier": "9780312367541",
                        }
                    ],
                    "description": "A classic novel.",
                }
            },
            {
                "volumeInfo": {
                    "title": "A Wrinkle in Time: Graphic Novel",
                    "authors": [
                        "Madeleine L'Engle"
                    ],
                }
            },
        ]
    }

    candidates = (
        GoogleBooksBookCandidateService
        ._create_candidates(data)
    )

    assert len(candidates) == 2
    assert all(
        isinstance(candidate, BookCandidate)
        for candidate in candidates
    )

    assert (
        candidates[0].book.title
        == "A Wrinkle in Time"
    )

    assert (
        candidates[0].book.isbn
        == "9780312367541"
    )

    assert (
        candidates[1].book.title
        == "A Wrinkle in Time: Graphic Novel"
    )


def test_create_candidates_with_no_items() -> None:
    candidates = (
        GoogleBooksBookCandidateService
        ._create_candidates({})
    )

    assert candidates == []


def test_find_candidates_raises_service_error_on_timeout(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def mock_get(*args, **kwargs):
        raise httpx.TimeoutException(
            "timeout"
        )

    monkeypatch.setattr(
        httpx,
        "get",
        mock_get,
    )

    service = GoogleBooksBookCandidateService(
        api_key="test-key",
    )

    with pytest.raises(
        BookInformationServiceError,
        match="timed out",
    ):
        service.find_candidates(
            BookInput(title="A Wrinkle in Time")
        )