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


def test_build_query_uses_title_even_when_author_is_provided() -> None:
    book = BookInput(
        title="A Wrinkle in Time",
        author="Madeleine L'Engle",
    )

    query = (
        GoogleBooksBookCandidateService
        ._build_query(book)
    )

    assert query == 'intitle:"A Wrinkle in Time"'


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
                    "title": (
                        "A Wrinkle in Time: Graphic Novel"
                    ),
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
            BookInput(
                title="A Wrinkle in Time"
            )
        )


def test_find_candidates_combines_results_from_multiple_queries(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = GoogleBooksBookCandidateService(
        api_key="test-key",
    )

    responses = [
        {
            "items": [
                {
                    "volumeInfo": {
                        "title": (
                            "Pemmican Wars "
                            "(A Girl Called Echo, Vol. 1)."
                        ),
                    }
                }
            ]
        },
        {
            "items": [
                {
                    "volumeInfo": {
                        "title": "Pemmican Wars",
                        "authors": [
                            "Katherena Vermette"
                        ],
                        "industryIdentifiers": [
                            {
                                "type": "ISBN_13",
                                "identifier": (
                                    "9781553797357"
                                ),
                            }
                        ],
                    }
                }
            ]
        },
        {
            "items": [
                {
                    "volumeInfo": {
                        "title": "Another Book",
                        "authors": [
                            "Another Author"
                        ],
                    }
                }
            ]
        },
    ]

    calls = []

    def mock_get(*args, **kwargs):
        calls.append(
            kwargs["params"]["q"]
        )

        response = httpx.Response(
            status_code=200,
            json=responses[len(calls) - 1],
            request=httpx.Request(
                "GET",
                "https://www.googleapis.com/"
                "books/v1/volumes",
            ),
        )

        return response

    monkeypatch.setattr(
        httpx,
        "get",
        mock_get,
    )

    candidates = service.find_candidates(
        BookInput(
            title="A Girl Called Echo Vol. 1",
            author="Katherena Vermette",
        )
    )

    assert len(candidates) == 3

    assert (
        candidates[0].book.title
        == "Pemmican Wars "
        "(A Girl Called Echo, Vol. 1)."
    )

    assert (
        candidates[1].book.title
        == "Pemmican Wars"
    )

    assert (
        candidates[1].book.author
        == "Katherena Vermette"
    )

    assert (
        candidates[2].book.title
        == "Another Book"
    )

    assert calls == [
        'intitle:"A Girl Called Echo Vol. 1"',
        "A Girl Called Echo Vol. 1",
        (
            'intitle:"A Girl Called Echo Vol. 1" '
            'inauthor:"Katherena Vermette"'
        ),
    ]

def test_create_candidates_extracts_series_evidence() -> None:
    data = {
        "items": [
            {
                "volumeInfo": {
                    "title": (
                        "Pemmican Wars "
                        "(A Girl Called Echo, Vol. 1)."
                    ),
                    "description": (
                        "Pemmican Wars is the first graphic novel "
                        "in a new series, A Girl Called Echo, "
                        "by Governor General Award-winning writer "
                        "Katherena Vermette."
                    ),
                }
            }
        ]
    }

    candidates = (
        GoogleBooksBookCandidateService
        ._create_candidates(data)
    )

    candidate = candidates[0]
    assert candidate.evidence is not None
    assert candidate.evidence.series_title == "A Girl Called Echo"
    assert candidate.evidence.volume_number == 1
    assert candidate.evidence.author == "Katherena Vermette"
    assert candidate.evidence.canonical_title == "Pemmican Wars"

def test_extract_author_ignores_fictitious_characters() -> None:
    authors = [
        "Dav Pilkey",
        "George Beard (Fictitious character)",
        "Harold Hutchins (Fictitious character)",
    ]

    result = GoogleBooksBookCandidateService._extract_author(
        authors
    )

    assert result == "Dav Pilkey"

def test_extract_author_preserves_multiple_real_authors() -> None:
    authors = [
        "Author One",
        "Author Two",
    ]

    result = GoogleBooksBookCandidateService._extract_author(
        authors
    )

    assert result == "Author One, Author Two"