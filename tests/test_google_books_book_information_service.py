import pytest
import httpx
import time

from unittest.mock import Mock, patch

from bookmatch.models.book import BookInput
from bookmatch.services.google_books_book_information_service import (
    GoogleBooksBookInformationService,
)

from bookmatch.services.exceptions import (
    BookInformationServiceError,
)

def test_enrich_by_isbn_returns_enriched_book() -> None:
    response = Mock()

    response.json.return_value = {
        "items": [
            {
                "volumeInfo": {
                    "title": "Charlotte's Web",
                    "authors": ["E. B. White"],
                    "publishedDate": "1952-10-15",
                    "description": "A story about a pig named Wilbur.",
                    "industryIdentifiers": [
                        {
                            "type": "ISBN_13",
                            "identifier": "9780064400558",
                        }
                    ],
                }
            }
        ]
    }

    service = GoogleBooksBookInformationService()

    book = BookInput(
        title="Charlotte's Web",
        author="E. B. White",
        isbn="9780064400558",
    )

    with patch(
        "bookmatch.services.google_books_book_information_service.httpx.get",
        return_value=response,
    ) as mock_get:
        result = service.enrich(book)

    mock_get.assert_called_once_with(
        service.BASE_URL,
        params={
            "q": "isbn:9780064400558",
        },
        timeout=10.0,
    )

    assert result.title == "Charlotte's Web"
    assert result.author == "E. B. White"
    assert result.publication_date == "1952-10-15"
    assert result.isbn == "9780064400558"
    assert result.description == "A story about a pig named Wilbur."
    assert result.source == "Google Books"

def test_enrich_by_isbn_raises_error_when_book_not_found() -> None:
    response = Mock()

    response.json.return_value = {
        "totalItems": 0,
    }

    service = GoogleBooksBookInformationService()

    book = BookInput(
        title="Some Unknown Book",
        isbn="0000000000000",
    )

    with patch(
        "bookmatch.services.google_books_book_information_service.httpx.get",
        return_value=response,
    ):
        with pytest.raises(
            BookInformationServiceError,
            match="Could not find book",
        ):
            service.enrich(book)

def test_enrich_by_title_returns_enriched_book() -> None:
    response = Mock()

    response.json.return_value = {
        "items": [
            {
                "volumeInfo": {
                    "title": "Charlotte's Web",
                    "authors": ["E. B. White"],
                    "publishedDate": "1952-10-15",
                    "description": "A story about a pig named Wilbur.",
                    "industryIdentifiers": [
                        {
                            "type": "ISBN_13",
                            "identifier": "9780064400558",
                        }
                    ],
                }
            }
        ]
    }

    service = GoogleBooksBookInformationService()

    book = BookInput(
        title="Charlotte's Web",
    )

    with patch(
        "bookmatch.services.google_books_book_information_service.httpx.get",
        return_value=response,
    ) as mock_get:
        result = service.enrich(book)

    mock_get.assert_called_once_with(
        service.BASE_URL,
        params={
            "q": 'intitle:"Charlotte\'s Web"',
        },
        timeout=10.0,
    )

    assert result.title == "Charlotte's Web"
    assert result.author == "E. B. White"
    assert result.description == "A story about a pig named Wilbur."
    assert result.source == "Google Books"

def test_enrich_by_title_and_author_returns_enriched_book() -> None:
    response = Mock()

    response.json.return_value = {
        "items": [
            {
                "volumeInfo": {
                    "title": "Charlotte's Web",
                    "authors": ["E. B. White"],
                    "publishedDate": "1952-10-15",
                    "description": "A story about a pig named Wilbur.",
                    "industryIdentifiers": [
                        {
                            "type": "ISBN_13",
                            "identifier": "9780064400558",
                        }
                    ],
                }
            }
        ]
    }

    service = GoogleBooksBookInformationService()

    book = BookInput(
        title="Charlotte's Web",
        author="E. B. White",
    )

    with patch(
        "bookmatch.services.google_books_book_information_service.httpx.get",
        return_value=response,
    ) as mock_get:
        result = service.enrich(book)

    mock_get.assert_called_once_with(
        service.BASE_URL,
        params={
            "q": 'intitle:"Charlotte\'s Web"+inauthor:"E. B. White"',
        },
        timeout=10.0,
    )

    assert result.title == "Charlotte's Web"
    assert result.author == "E. B. White"
    assert result.description == "A story about a pig named Wilbur."
    assert result.source == "Google Books"

def test_get_retries_on_429_and_succeeds() -> None:
    response_429 = Mock()
    response_429.headers = {}
    response_429.raise_for_status.side_effect = (
        httpx.HTTPStatusError(
            "429 Too Many Requests",
            request=Mock(),
            response=Mock(
                status_code=429,
                headers={},
            ),
        )
    )

    response_success = Mock()
    response_success.raise_for_status.return_value = None

    service = GoogleBooksBookInformationService()

    with patch(
        "bookmatch.services.google_books_book_information_service.httpx.get",
        side_effect=[
            response_429,
            response_429,
            response_success,
        ],
    ) as mock_get:
        with patch(
            "bookmatch.services.google_books_book_information_service.time.sleep"
        ) as mock_sleep:
            result = service._get(service.BASE_URL)

    assert result is response_success

    assert mock_get.call_count == 3
    mock_sleep.assert_any_call(1)
    mock_sleep.assert_any_call(2)

def test_get_uses_retry_after_header() -> None:
    response_429 = Mock()
    response_429.headers = {
        "Retry-After": "5",
    }
    response_429.raise_for_status.side_effect = (
        httpx.HTTPStatusError(
            "429 Too Many Requests",
            request=Mock(),
            response=Mock(
                status_code=429,
                headers={
                    "Retry-After": "5",
                },
            ),
        )
    )

    response_success = Mock()
    response_success.raise_for_status.return_value = None

    service = GoogleBooksBookInformationService()

    with patch(
        "bookmatch.services.google_books_book_information_service.httpx.get",
        side_effect=[
            response_429,
            response_success,
        ],
    ) as mock_get:
        with patch(
            "bookmatch.services.google_books_book_information_service.time.sleep"
        ) as mock_sleep:
            with patch(
                "bookmatch.services.google_books_book_information_service.time.monotonic",
                side_effect=[
                    100.0,
                    100.0,
                    105.0,
                    105.0,
                ],
            ):
                result = service._get(service.BASE_URL)

    assert result is response_success

    assert mock_get.call_count == 2
    mock_sleep.assert_called_once_with(5.0)

def test_get_throttles_requests() -> None:
    response_1 = Mock()
    response_1.raise_for_status.return_value = None

    response_2 = Mock()
    response_2.raise_for_status.return_value = None

    service = GoogleBooksBookInformationService()

    with patch(
        "bookmatch.services.google_books_book_information_service.httpx.get",
        side_effect=[
            response_1,
            response_2,
        ],
    ) as mock_get:
        with patch(
            "bookmatch.services.google_books_book_information_service.time.sleep"
        ) as mock_sleep:
            with patch(
                "bookmatch.services.google_books_book_information_service.time.monotonic",
                side_effect=[
                    100.0,
                    100.0,
                    100.5,
                    100.5,
                ],
            ):
                service._get(service.BASE_URL)
                service._get(service.BASE_URL)

    assert mock_get.call_count == 2
    mock_sleep.assert_called_once_with(0.5)

