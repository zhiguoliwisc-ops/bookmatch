from unittest.mock import Mock, patch

import httpx
import pytest

from bookmatch.models.book import BookInput
from bookmatch.services.exceptions import (
    BookInformationServiceError,
)
from bookmatch.services.open_library_book_candidate_service import (
    OpenLibraryBookCandidateService,
)


def test_find_candidates_by_isbn_returns_candidate() -> None:
    response = Mock()
    response.status_code = 200
    response.json.return_value = {
        "title": "Charlotte's Web",
        "description": {
            "value": "A story about a pig and a spider.",
        },
    }

    service = OpenLibraryBookCandidateService()

    book = BookInput(
        title="Charlotte's Web",
        author="E. B. White",
        isbn="9780064400558",
    )

    with patch(
        "bookmatch.services.open_library_book_candidate_service.httpx.get",
        return_value=response,
    ) as mock_get:
        result = service.find_candidates(book)

    mock_get.assert_called_once_with(
        "https://openlibrary.org/isbn/9780064400558.json",
        headers=service.HEADERS,
        timeout=10.0,
        follow_redirects=True,
    )

    assert len(result) == 1
    assert result[0].provider == "Open Library"
    assert result[0].book.title == "Charlotte's Web"
    assert result[0].book.author == "E. B. White"
    assert result[0].book.isbn == "9780064400558"
    assert result[0].book.description == (
        "A story about a pig and a spider."
    )


def test_isbn_404_falls_back_to_title_and_author() -> None:
    isbn_response = Mock()
    isbn_response.status_code = 404

    search_response = Mock()
    search_response.status_code = 200
    search_response.json.return_value = {
        "docs": [
            {
                "title": "Charlotte's Web",
                "author_name": ["E. B. White"],
                "first_publish_year": 1952,
                "isbn": ["9780064400558"],
            }
        ]
    }

    service = OpenLibraryBookCandidateService()

    book = BookInput(
        title="Charlotte's Web",
        author="E. B. White",
        isbn="9780064400558",
    )

    with patch(
        "bookmatch.services.open_library_book_candidate_service.httpx.get",
        side_effect=[
            isbn_response,
            search_response,
        ],
    ) as mock_get:
        result = service.find_candidates(book)

    assert mock_get.call_count == 2

    assert result[0].book.title == "Charlotte's Web"
    assert result[0].book.author == "E. B. White"
    assert result[0].book.publication_date == "1952"


def test_find_candidates_by_title_and_author_returns_multiple_candidates() -> None:
    response = Mock()
    response.status_code = 200
    response.json.return_value = {
        "docs": [
            {
                "title": "The Outsiders",
                "author_name": ["S. E. Hinton"],
                "first_publish_year": 1967,
                "isbn": ["9780140385724"],
            },
            {
                "title": "The Outsiders",
                "author_name": ["S. E. Hinton"],
                "first_publish_year": 1988,
                "isbn": ["9780671722170"],
            },
        ]
    }

    service = OpenLibraryBookCandidateService()

    book = BookInput(
        title="The Outsiders",
        author="S. E. Hinton",
    )

    with patch(
        "bookmatch.services.open_library_book_candidate_service.httpx.get",
        return_value=response,
    ) as mock_get:
        result = service.find_candidates(book)

    mock_get.assert_called_once_with(
        "https://openlibrary.org/search.json",
        headers=service.HEADERS,
        timeout=10.0,
        follow_redirects=True,
        params={
            "title": "The Outsiders",
            "author": "S. E. Hinton",
        },
    )

    assert len(result) == 2
    assert result[0].book.title == "The Outsiders"
    assert result[1].book.title == "The Outsiders"

    assert result[0].provider == "Open Library"
    assert result[1].provider == "Open Library"


def test_title_search_with_no_results_returns_empty_list() -> None:
    response = Mock()
    response.status_code = 200
    response.json.return_value = {
        "docs": [],
    }

    service = OpenLibraryBookCandidateService()

    book = BookInput(
        title="Unknown Book",
        author="Unknown Author",
    )

    with patch(
        "bookmatch.services.open_library_book_candidate_service.httpx.get",
        return_value=response,
    ):
        result = service.find_candidates(book)

    assert result == []


def test_timeout_raises_book_information_service_error() -> None:
    service = OpenLibraryBookCandidateService()

    book = BookInput(
        title="Charlotte's Web",
        author="E. B. White",
    )

    with patch(
        "bookmatch.services.open_library_book_candidate_service.httpx.get",
        side_effect=httpx.TimeoutException(
            "Request timed out"
        ),
    ):
        with pytest.raises(
            BookInformationServiceError,
            match="timed out",
        ):
            service.find_candidates(book)


def test_request_error_raises_book_information_service_error() -> None:
    service = OpenLibraryBookCandidateService()

    book = BookInput(
        title="Charlotte's Web",
        author="E. B. White",
    )

    with patch(
        "bookmatch.services.open_library_book_candidate_service.httpx.get",
        side_effect=httpx.RequestError(
            "Connection failed"
        ),
    ):
        with pytest.raises(
            BookInformationServiceError,
            match="Could not connect",
        ):
            service.find_candidates(book)


def test_invalid_json_raises_book_information_service_error() -> None:
    response = Mock()
    response.status_code = 200
    response.json.side_effect = ValueError(
        "Invalid JSON"
    )

    service = OpenLibraryBookCandidateService()

    book = BookInput(
        title="Charlotte's Web",
        author="E. B. White",
    )

    with patch(
        "bookmatch.services.open_library_book_candidate_service.httpx.get",
        return_value=response,
    ):
        with pytest.raises(
            BookInformationServiceError,
            match="invalid response",
        ):
            service.find_candidates(book)


def test_http_error_raises_book_information_service_error() -> None:
    response = Mock()
    response.status_code = 503

    request = Mock()

    http_error = httpx.HTTPStatusError(
        "503 Service Unavailable",
        request=request,
        response=response,
    )

    response.raise_for_status.side_effect = http_error

    service = OpenLibraryBookCandidateService()

    book = BookInput(
        title="Charlotte's Web",
        author="E. B. White",
    )

    with patch(
        "bookmatch.services.open_library_book_candidate_service.httpx.get",
        return_value=response,
    ):
        with pytest.raises(
            BookInformationServiceError,
            match="503",
        ):
            service.find_candidates(book)